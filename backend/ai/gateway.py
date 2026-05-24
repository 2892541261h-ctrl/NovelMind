"""统一 AI 调用入口 - v1.3: supports configurable providers, usage logging, cost estimation."""

import json
import os
import time
import urllib.request
import urllib.error

from .types import AIRequest, AIResponse


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
            from .provider_factory import get_provider as get_mock_provider
            provider = get_mock_provider(None)
            response = await provider.generate(request)
        elif provider_type == "oai_compat":
            response = _call_oai_compat(request, model_name, base_url, env_var)
        else:
            from .provider_factory import get_provider as get_mock_provider
            provider = get_mock_provider(None)
            response = await provider.generate(request)

        latency_ms = int((time.time() - t0) * 1000)
        _log_usage(feature_name, provider_type, model_name, "success",
                   response.usage.get("prompt_tokens"), response.usage.get("completion_tokens"),
                   response.usage.get("total_tokens"), provider_id, model_cfg_id, latency_ms,
                   _trunc(str(request.messages[0].content) if request.messages else "", 500),
                   _trunc(response.content, 500))
        response.model = model_name
        response.provider = provider_type
        return response

    except Exception as exc:
        latency_ms = int((time.time() - t0) * 1000) if 't0' in dir() else 0
        _log_usage(feature_name, "unknown", request.model or "unknown", "error",
                   None, None, None, None, None, latency_ms, error_message=str(exc)[:500])
        return AIResponse(provider="unknown", model=request.model or "unknown",
                          content="", raw={}, usage={}, error=str(exc))


def _call_oai_compat(request: AIRequest, model: str, base_url: str, env_var: str) -> AIResponse:
    api_key = os.environ.get(env_var, "")
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
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return AIResponse(provider="oai_compat", model=model, content="",
                          raw={"error": body_text[:500]}, usage={}, error=f"HTTP {e.code}: {body_text[:200]}")
    except Exception as e:
        return AIResponse(provider="oai_compat", model=model, content="",
                          raw={}, usage={}, error=str(e))

    choice = (raw.get("choices") or [{}])[0]
    content = choice.get("message", {}).get("content", "")
    usage_data = raw.get("usage", {})
    return AIResponse(
        provider="oai_compat", model=model, content=content, raw=raw,
        usage={
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
        }, error=None,
    )


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
