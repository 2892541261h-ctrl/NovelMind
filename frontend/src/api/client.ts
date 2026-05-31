// 桌面端 / 生产环境：同源托管，使用相对路径（空字符串）
// 开发环境：通过 VITE_API_BASE_URL 设置，例如 http://localhost:8765
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export function getBaseUrl(): string {
  return BASE_URL;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${msg || res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

import type {
  Project, ProjectCreate,
  Character, CharacterCreate,
  Chapter, ChapterCreate,
  HealthResponse, AIResponse,
} from "../types/api";

// Health & AI
export function healthCheck() { return request<HealthResponse>("/health"); }
export function testAI() { return request<AIResponse>("/api/ai/test"); }

// Projects
export function getProjects() { return request<Project[]>("/api/projects"); }
export function getProject(id: number) { return request<Project>(`/api/projects/${id}`); }
export function createProject(data: ProjectCreate) {
  return request<Project>("/api/projects", { method: "POST", body: JSON.stringify(data) });
}
export function updateProject(id: number, data: Partial<ProjectCreate>) {
  return request<Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(data) });
}
export function deleteProject(id: number) {
  return request<void>(`/api/projects/${id}`, { method: "DELETE" });
}

// Characters
export function getProjectCharacters(projectId: number) {
  return request<Character[]>(`/api/projects/${projectId}/characters`);
}
export function createCharacter(projectId: number, data: CharacterCreate) {
  return request<Character>(`/api/projects/${projectId}/characters`, {
    method: "POST", body: JSON.stringify({ ...data, project_id: projectId }),
  });
}
export function deleteCharacter(id: number) {
  return request<void>(`/api/characters/${id}`, { method: "DELETE" });
}

// Chapters
export function getProjectChapters(projectId: number) {
  return request<Chapter[]>(`/api/projects/${projectId}/chapters`);
}
export function createChapter(projectId: number, data: ChapterCreate) {
  return request<Chapter>(`/api/projects/${projectId}/chapters`, {
    method: "POST", body: JSON.stringify({ ...data, project_id: projectId }),
  });
}
export function deleteChapter(id: number) {
  return request<void>(`/api/chapters/${id}`, { method: "DELETE" });
}
