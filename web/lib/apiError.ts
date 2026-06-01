type FastApiDetailItem = { msg?: string; type?: string };

type FastApiErrorBody = {
  detail?: string | FastApiDetailItem[];
};

/** Map FastAPI `detail` (string or 422 validation array) to a user-visible message. */
export function apiErrorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const detail = (body as FastApiErrorBody).detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const msgs = detail
      .map((item) => (typeof item?.msg === "string" ? item.msg : ""))
      .filter(Boolean);
    if (msgs.length > 0) return msgs.join("；");
  }
  return fallback;
}
