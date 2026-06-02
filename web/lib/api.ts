import { apiErrorMessage } from "@/lib/apiError";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8787";
const API_PREFIX = process.env.NEXT_PUBLIC_API_PREFIX || "";

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${API_PREFIX}${p}`;
}

export type SessionStatus = "pending" | "processing" | "ready" | "failed";

export interface DiagnosisResult {
  jd_interpretation: {
    role_summary: string;
    hard_requirements: string[];
    preferred_requirements: string[];
    keywords: string[];
    responsibilities: string[];
    nice_to_have: string[];
  };
  match_score: {
    overall: number;
    status: string;
    breakdown: Record<string, number>;
  };
  gap_report: {
    matched: string[];
    partial_match: { requirement: string; severity: string; suggestion: string }[];
    hard_missing: { requirement: string; severity: string; suggestion: string }[];
    preferred_missing: { requirement: string; severity: string; suggestion: string }[];
    keyword_missing: string[];
    total_gaps: number;
  };
  changes: {
    id: string;
    section: string;
    original: string;
    revised: string;
    reason: string;
    evidence_ids: string[];
    risk_level: string;
    status: string;
    requires_user_confirmation: boolean;
    source_label: string;
  }[];
  policy_guard?: {
    passed: boolean;
    blocked_count: number;
    warnings: string[];
  };
  free_change_limit?: number;
}

export type CreateSessionInput = {
  jdText: string;
  consent?: boolean;
  resume?: File | null;
  resumeText?: string;
};

/** True when the API message suggests DOCX parse failure — show paste fallback UI. */
export function isResumeParseError(message: string): boolean {
  return /解析|\.docx|简历全文|无法从 DOCX|上传.*粘贴/i.test(message);
}

export async function createSession(
  input: CreateSessionInput,
): Promise<{ session_id: string }> {
  const form = new FormData();
  if (input.resume) {
    form.append("resume", input.resume);
  }
  const pasted = input.resumeText?.trim();
  if (pasted) {
    form.append("resume_text", pasted);
  }
  form.append("jd_text", input.jdText);
  form.append("consent", input.consent !== false ? "true" : "false");
  const res = await fetch(apiUrl("/sessions"), { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const fallback =
      res.status === 429 ? "今日创建会话次数已达上限，请明天再试。" : res.statusText;
    throw new Error(apiErrorMessage(err, fallback));
  }
  return res.json();
}

export async function getSession(sessionId: string): Promise<{
  session_id: string;
  status: SessionStatus;
  result: DiagnosisResult | null;
  error: string | null;
  processing_step?: string | null;
}> {
  const res = await fetch(apiUrl(`/sessions/${sessionId}`));
  if (!res.ok) throw new Error("会话不存在或已过期");
  return res.json();
}

export type ChangePatchBody = {
  status?: "accepted" | "rejected" | "pending";
  revised?: string;
};

export async function patchChange(
  sessionId: string,
  changeId: string,
  body: ChangePatchBody,
): Promise<void> {
  const res = await fetch(apiUrl(`/sessions/${sessionId}/changes/${changeId}`), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(apiErrorMessage(err, "更新失败"));
  }
}

export async function exportSession(
  sessionId: string,
): Promise<{ download_url: string; format: "docx" | "txt" }> {
  const res = await fetch(apiUrl(`/sessions/${sessionId}/export`), { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(apiErrorMessage(err, "导出失败"));
  }
  return res.json();
}

export function exportDownloadUrl(sessionId: string, path: string): string {
  return apiUrl(path);
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(apiUrl(`/sessions/${sessionId}`), { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(apiErrorMessage(err, "删除失败"));
  }
}
