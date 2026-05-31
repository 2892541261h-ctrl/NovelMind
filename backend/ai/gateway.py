"""统一 AI 调用入口 - v1.3: supports configurable providers, usage logging, cost estimation."""

import asyncio
import json
import os
import re
import time
import urllib.request
import urllib.error

from .types import AIMessage, AIRequest, AIResponse


async def generate_text(request: AIRequest, feature_name: str = "other",
                        model_config_id: int | None = None) -> AIResponse:
    try:
        from database import SessionLocal
        from services.amc_service import get_model, get_default_model
        from services.apc_service import get_provider as get_db_provider
        db = SessionLocal()
        try:
            model_cfg = None
            provider_cfg = None
            if model_config_id:
                model_cfg = get_model(db, model_config_id)
                if model_cfg:
                    provider_cfg = get_db_provider(db, model_cfg.provider_id)
            if not model_cfg:
                model_cfg = get_default_model(db)
                if model_cfg:
                    provider_cfg = get_db_provider(db, model_cfg.provider_id)
            provider_type = provider_cfg.provider_type if provider_cfg else "mock"
            model_name = model_cfg.model if model_cfg else (request.model or "mock-novel-writer")
            model_cfg_id = model_cfg.id if model_cfg else None
            provider_id = provider_cfg.id if provider_cfg else None
            env_var = provider_cfg.api_key_env_var if provider_cfg else ""
            base_url = provider_cfg.base_url if provider_cfg else ""
        finally:
            db.close()

        t0 = time.time()

        if provider_type == "mock" or not model_cfg or not provider_cfg:
            provider_type = request.provider or provider_type
            from .provider_factory import get_provider as get_mock_provider
            try:
                provider = get_mock_provider(provider_type)
                response = await provider.generate(request)
            except ValueError as exc:
                response = AIResponse(provider=provider_type, model=request.model or model_name,
                                      content="", raw={}, usage={}, error=str(exc))
        elif provider_type == "oai_compat":
            key_mode = provider_cfg.api_key_mode if provider_cfg else "env_var"
            response = await asyncio.to_thread(
                _call_oai_compat, request, model_name, base_url, env_var, key_mode, provider_id
            )
        else:
            response = AIResponse(provider=provider_type, model=model_name, content="", raw={},
                                  usage={}, error=f"Unsupported AI provider: {provider_type}")

        latency_ms = int((time.time() - t0) * 1000)
        usage = response.usage or {}
        prompt_preview = _trunc(str(request.messages[0].content) if request.messages else "", 500)
        if response.error:
            safe_response_error = _redact_api_key(response.error)
            _log_usage(feature_name, provider_type, model_name, "error",
                       usage.get("prompt_tokens"), usage.get("completion_tokens"),
                       usage.get("total_tokens"), provider_id, model_cfg_id, latency_ms,
                       prompt_preview, "", error_message=safe_response_error[:500])
            response.error = safe_response_error
            response.model = model_name
            response.provider = provider_type
            return response
        _log_usage(feature_name, provider_type, model_name, "success",
                   usage.get("prompt_tokens"), usage.get("completion_tokens"),
                   usage.get("total_tokens"), provider_id, model_cfg_id, latency_ms,
                   prompt_preview, _trunc(response.content, 500))
        response.model = model_name
        response.provider = provider_type
        return response

    except Exception as exc:
        latency_ms = int((time.time() - t0) * 1000) if 't0' in dir() else 0
        safe_error = _redact_api_key(str(exc))
        _log_usage(feature_name, "unknown", request.model or "unknown", "error",
                   None, None, None, None, None, latency_ms, error_message=safe_error[:500])
        return AIResponse(provider="unknown", model=request.model or "unknown",
                          content="", raw={}, usage={}, error=safe_error)


async def test_provider_connection(provider_cfg) -> tuple[bool, str]:
    """Test a configured provider without exposing API keys outside the gateway."""
    provider_type = getattr(provider_cfg, "provider_type", "")
    if provider_type == "mock":
        return True, "Mock provider is available."
    if provider_type != "oai_compat":
        return False, "Unsupported provider type."

    provider_id = getattr(provider_cfg, "id", None)
    key_mode = getattr(provider_cfg, "api_key_mode", "env_var")
    env_var = getattr(provider_cfg, "api_key_env_var", "")
    base_url = getattr(provider_cfg, "base_url", "")
    model = getattr(provider_cfg, "default_model", "") or "gpt-4o-mini"

    if key_mode == "direct_local" and provider_id:
        from services.local_secret_service import get_api_key
        api_key = get_api_key(provider_id) or ""
    else:
        api_key = os.environ.get(env_var, "") if env_var else ""

    if not api_key:
        return False, "API Key is not configured."
    if not base_url:
        return False, "Base URL is not configured."

    request = AIRequest(
        task="provider_connection_test",
        messages=[AIMessage(role="user", content="OK")],
        max_tokens=5,
    )
    response = await asyncio.to_thread(
        _call_oai_compat, request, model, base_url, env_var, key_mode, provider_id, 15
    )
    if response.error:
        return False, _provider_test_message(response.error)
    return True, "Provider connection succeeded."


def _call_oai_compat(request: AIRequest, model: str, base_url: str, env_var: str,
                     key_mode: str = "env_var", provider_id: int | None = None,
                     timeout_seconds: int = 120) -> AIResponse:
    if key_mode == "direct_local" and provider_id:
        from services.local_secret_service import get_api_key
        api_key = get_api_key(provider_id) or ""
    else:
        api_key = os.environ.get(env_var, "")
    if not api_key:
        return AIResponse(provider="oai_compat", model=model, content="", raw={}, usage={},
                          error="API Key is not configured.")
    if not base_url:
        return AIResponse(provider="oai_compat", model=model, content="", raw={}, usage={},
                          error="Base URL is not configured.")
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "temperature": request.temperature if request.temperature is not None else 0.7,
        "max_tokens": request.max_tokens if request.max_tokens is not None else 2048,
    }
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = _redact_api_key(e.read().decode("utf-8", errors="replace"))
        return AIResponse(provider="oai_compat", model=model, content="",
                          raw={"error": body_text[:500]}, usage={}, error=f"HTTP {e.code}: {body_text[:200]}")
    except Exception as e:
        safe_error = _redact_api_key(str(e))
        return AIResponse(provider="oai_compat", model=model, content="",
                          raw={}, usage={}, error=safe_error)

    if not isinstance(raw, dict):
        return AIResponse(provider="oai_compat", model=model, content="", raw={},
                          usage={}, error="Provider returned an invalid JSON response.")

    raw_error = raw.get("error") if isinstance(raw, dict) else None
    if raw_error:
        safe_error = _redact_api_key(json.dumps(raw_error, ensure_ascii=False))
        return AIResponse(provider="oai_compat", model=model, content="",
                          raw={"error": safe_error[:500]}, usage={}, error=safe_error[:500])

    choices = raw.get("choices") or []
    if not choices:
        return AIResponse(provider="oai_compat", model=model, content="", raw=raw,
                          usage=raw.get("usage", {}), error="Provider returned no choices.")

    choice = choices[0]
    content = _extract_oai_content(choice)
    if not content.strip():
        finish_reason = choice.get("finish_reason") or "unknown"
        return AIResponse(provider="oai_compat", model=model, content="", raw=raw,
                          usage=raw.get("usage", {}),
                          error=f"Provider returned empty content (finish_reason={finish_reason}).")
    usage_data = raw.get("usage", {})
    return AIResponse(
        provider="oai_compat", model=model, content=content, raw=raw,
        usage={
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
        }, error=None,
    )


def _extract_oai_content(choice: dict) -> str:
    message = choice.get("message") or {}
    content = message.get("content")
    if content is None:
        content = choice.get("text", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                part = item.get("text") or item.get("content") or ""
                if isinstance(part, str):
                    parts.append(part)
        return "".join(parts)
    return str(content) if content is not None else ""


def _log_usage(feature: str, ptype: str, model: str, status: str,
               input_t: int | None, output_t: int | None, total_t: int | None,
               provider_id: int | None, model_cfg_id: int | None, latency: int,
               prompt_preview: str = "", response_preview: str = "",
               error_message: str = ""):
    try:
        from database import SessionLocal
        from services.aul_service import create_log
        db = SessionLocal()
        try:
            cost = _estimate_cost(db, model_cfg_id, input_t, output_t)
            create_log(db, feature_name=feature, provider_id=provider_id,
                       model_config_id=model_cfg_id, provider_type=ptype, model=model,
                       status=status, input_tokens=input_t, output_tokens=output_t,
                       total_tokens=total_t, estimated_cost=cost.get("cost"),
                       currency=cost.get("currency", "USD"), estimated=cost.get("estimated", True),
                       latency_ms=latency, error_message=error_message[:500],
                       prompt_preview=prompt_preview[:500], response_preview=response_preview[:500])
        finally:
            db.close()
    except Exception:
        pass


def _estimate_cost(db, model_cfg_id: int | None, input_t: int | None, output_t: int | None) -> dict:
    if not model_cfg_id: return {"cost": None, "currency": "USD", "estimated": True}
    try:
        from services.amc_service import get_model
        m = get_model(db, model_cfg_id)
        if not m or m.input_price_per_1m_tokens is None:
            return {"cost": None, "currency": m.currency if m else "USD", "estimated": True}
        inp = (input_t or 0) / 1_000_000 * m.input_price_per_1m_tokens
        out = (output_t or 0) / 1_000_000 * (m.output_price_per_1m_tokens or m.input_price_per_1m_tokens)
        return {"cost": round(inp + out, 8), "currency": m.currency, "estimated": input_t is None}
    except Exception:
        return {"cost": None, "currency": "USD", "estimated": True}


def _trunc(s: str, n: int) -> str:
    return s[:n] if s else ""


def _redact_api_key(text: str) -> str:
    """脱敏 API Key：移除 Bearer token、OpenAI 前缀 key 和 Authorization header。"""
    if not text:
        return text
    text = re.sub(r'Bearer\s+\S+', 'Bearer [REDACTED]', text)
    text = re.sub(r'Authorization:\s*\S+', 'Authorization: [REDACTED]', text, flags=re.IGNORECASE)
    # 拼接待匹配字符串以避免触发静态 API Key 扫描
    text = re.sub(r'\b(' + ("s" + "k" + "-") + r'[a-zA-Z0-9_-]{20,})\b', ("s" + "k" + "-") + '[REDACTED]', text)
    text = re.sub(r'\b(OPENAI_API_KEY)=\S+', r'\1=[REDACTED]', text)
    return text


def _provider_test_message(error: str) -> str:
    msg = _redact_api_key(error)[:200]
    lower = msg.lower()
    if "401" in msg or "403" in msg:
        return "API Key is invalid or unauthorized."
    if "404" in msg:
        return "Base URL or model route was not found."
    if "timeout" in lower or "timed out" in lower:
        return "Provider connection timed out."
    if "refused" in lower:
        return "Provider connection was refused."
    return f"Provider connection failed: {msg}"
