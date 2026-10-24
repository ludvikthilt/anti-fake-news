export type StatusKey = "corroboree" | "non_corroboree" | "contredite" | "indeterminee";

export interface Criterion {
  key: string;
  label: string;
  value: string;
  ok: boolean;
  explanation: string;
}

export interface SourceRow {
  url: string;
  domain: string;
  title: string;
  excerpt: string;
  type: string;
  score: number;
  position: string;
  date: string | null;
  date_origin: string;
  found_by: string;
}

export interface FactCheckRow {
  organization: string;
  verdict: string;
  url: string;
  published_date: string | null;
  summary: string;
  contradicts: boolean;
}

export interface CertificationRow {
  verdict: string;
  comment: string;
  source_url: string;
  created_at: string | null;
  insider: string;
}

export interface MissingService {
  service: string;
  reason: string;
}

export interface AnalysisResult {
  public_id: string;
  status: StatusKey;
  status_label: string;
  status_phrase: string;
  nature: string | null;
  disorder: string | null;
  extraction?: {
    source?: string;
    author?: string;
    title?: string;
    date?: string;
    date_origin?: string;
    keywords?: string[];
    ocr_text?: string;
    ocr_engine?: string;
    phash?: string;
    platform?: string;
    image_pending?: boolean;
    image_search?: string;
    image_tools?: { title: string; link: string; snippet?: string }[];
  };
  criteria: Criterion[];
  sources: SourceRow[];
  factchecks: FactCheckRow[];
  certifications: CertificationRow[];
  missing: MissingService[];
  created_at: string;
}

export interface AnalysisDetail {
  id: string;
  public_id: string;
  input_type: string;
  input_text?: string;
  input_url?: string;
  status: "pending" | "running" | "done" | "partial" | "failed";
  result: AnalysisResult;
  created_at: string;
  updated_at: string;
}

export interface UserInfo {
  id: number;
  email: string;
  name: string;
  role: "user" | "insider" | "admin";
  is_email_verified: boolean;
  date_joined: string;
}

export interface WikiListItem {
  slug: string;
  title: string;
  updated_at: string;
}

export interface WikiDetail {
  slug: string;
  title: string;
  content: string;
  published: boolean;
  author_name: string;
  updated_at: string;
}
