/** Daily cap on POST /api/sessions (edge). Keep detail in sync with server rate_limit.py */

export const RATE_LIMIT_DETAIL =
  "今日创建会话次数已达上限，请明天再试。";

type Bucket = { day: string; count: number };

const buckets = new Map<string, Bucket>();

function dayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

export function clientIp(request: Request): string {
  const cf = request.headers.get("CF-Connecting-IP");
  if (cf?.trim()) return cf.trim();
  const xff = request.headers.get("X-Forwarded-For");
  if (xff) {
    const first = xff.split(",")[0]?.trim();
    if (first) return first;
  }
  return "unknown";
}

/** Returns a 429 Response when limited; otherwise records this attempt and returns null. */
export function limitSessionCreate(
  request: Request,
  limit: number,
): Response | null {
  if (!Number.isFinite(limit) || limit <= 0) return null;

  const ip = clientIp(request);
  const day = dayKey();
  const key = `${ip}:${day}`;
  const entry = buckets.get(key);
  const count = entry?.day === day ? entry.count : 0;

  if (count >= limit) {
    return new Response(JSON.stringify({ detail: RATE_LIMIT_DETAIL }), {
      status: 429,
      headers: { "Content-Type": "application/json" },
    });
  }

  buckets.set(key, { day, count: count + 1 });
  return null;
}

/** @internal test helper */
export function _resetRateLimitBucketsForTests(): void {
  buckets.clear();
}
