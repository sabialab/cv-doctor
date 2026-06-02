/**
 * Daily cap on POST /api/sessions (edge). Keep detail in sync with server rate_limit.py.
 * P0: in-memory per isolate (best-effort). Durable KV/D1 counter is a follow-up for multi-isolate prod.
 */

export const RATE_LIMIT_DETAIL =
  "今日创建会话次数已达上限，请明天再试。";

type Bucket = { day: string; count: number };

const buckets = new Map<string, Bucket>();

function dayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function bucketKey(request: Request): string {
  return clientIp(request);
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

function currentCount(key: string, day: string): number {
  const entry = buckets.get(key);
  return entry?.day === day ? entry.count : 0;
}

/** Returns 429 when at cap; does not increment (record after upstream 2xx). */
export function checkSessionCreateLimit(
  request: Request,
  limit: number,
): Response | null {
  if (!Number.isFinite(limit) || limit <= 0) return null;

  const day = dayKey();
  const key = bucketKey(request);
  if (currentCount(key, day) >= limit) {
    return new Response(JSON.stringify({ detail: RATE_LIMIT_DETAIL }), {
      status: 429,
      headers: { "Content-Type": "application/json" },
    });
  }
  return null;
}

/** Count a successful session create (call after upstream returns 2xx). */
export function recordSessionCreate(request: Request): void {
  const day = dayKey();
  const key = bucketKey(request);
  const count = currentCount(key, day);
  buckets.set(key, { day, count: count + 1 });
}

/** @internal test helper */
export function _resetRateLimitBucketsForTests(): void {
  buckets.clear();
}
