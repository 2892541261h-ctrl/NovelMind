export interface Project {
  id: number;
  title: string;
  genre: string;
  description: string;
  target_word_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  title: string;
  genre?: string;
  description?: string;
  target_word_count?: number;
  status?: string;
}

export interface Character {
  id: number;
  project_id: number;
  name: string;
  age: number;
  gender: string;
  role_type: string;
  appearance: string;
  personality: string;
  background: string;
  goal: string;
  secret: string;
  speaking_style: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CharacterCreate {
  project_id: number;
  name: string;
  age?: number;
  gender?: string;
  role_type?: string;
  personality?: string;
  goal?: string;
}

export interface Chapter {
  id: number;
  project_id: number;
  chapter_number: number;
  title: string;
  goal: string;
  summary: string;
  content: string;
  involved_characters: string;
  location: string;
  conflict: string;
  ending_hook: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChapterCreate {
  project_id: number;
  chapter_number: number;
  title: string;
  goal?: string;
  summary?: string;
  content?: string;
}

export interface HealthResponse {
  status: string;
  app: string;
  ai_provider: string;
  database: string;
}

export interface AIResponse {
  request_id: string;
  provider: string;
  model: string;
  content: string;
  raw: Record<string, unknown>;
  usage: Record<string, unknown>;
  error: string | null;
}
