/**
 * P0 边缘 API 骨架：生产环境代理到 Container；本地可直连 PIPELINE_URL。
 */
import { Hono } from "hono";
import { cors } from "hono/cors";

import { checkSessionCreateLimit, recordSessionCreate } from "./rate_limit";

type Bindings = {
  PIPELINE_URL: string;
  ALLOWED_ORIGINS: string;
  RATE_LIMIT_SESSIONS_PER_DAY?: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use("*", async (c, next) => {
  const origins = (c.env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim());
  const allowList = origins.filter(Boolean);
  return cors({
    origin: allowList.length ? allowList : "*",
    allowMethods: ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type"],
    credentials: allowList.length > 0,
  })(c, next);
});

app.get("/health", (c) => c.json({ status: "ok", layer: "worker" }));

const _HOP_BY_HOP_HEADERS = [
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
];

function sanitizeUpstreamHeaders(upstream: Headers): Headers {
  const headers = new Headers(upstream);
  for (const key of _HOP_BY_HOP_HEADERS) {
    headers.delete(key);
  }
  headers.delete("content-encoding");
  headers.delete("content-length");
  return headers;
}

/** POST /api/sessions only — per-IP daily cap (Python skips when CF-Connecting-IP is set). */
app.use("/api/sessions", async (c, next) => {
  if (c.req.method !== "POST") {
    return next();
  }
  const parsed = parseInt(c.env.RATE_LIMIT_SESSIONS_PER_DAY ?? "20", 10);
  const limit = Number.isFinite(parsed) && parsed > 0 ? parsed : 20;
  const blocked = checkSessionCreateLimit(c.req.raw, limit);
  if (blocked) return blocked;
  await next();
  if (c.res.status >= 200 && c.res.status < 300) {
    recordSessionCreate(c.req.raw);
  }
});

/** 将 /api/* 转发到 Python 流水线（P0 本地与容器同路径） */
app.all("/api/*", async (c) => {
  const base = c.env.PIPELINE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8787";
  const path = c.req.path.replace(/^\/api/, "") || "/";
  const search = new URL(c.req.url).search;
  const url = `${base}${path}${search}`;

  const headers = new Headers(c.req.raw.headers);
  headers.delete("host");

  const init: RequestInit = {
    method: c.req.method,
    headers,
  };
  if (c.req.method !== "GET" && c.req.method !== "HEAD") {
    init.body = c.req.raw.body;
    // @ts-expect-error duplex for streaming body
    init.duplex = "half";
  }

  try {
    const upstream = await fetch(url, init);
    return new Response(upstream.body, {
      status: upstream.status,
      headers: sanitizeUpstreamHeaders(upstream.headers),
    });
  } catch {
    return c.text("上游服务不可用", 502);
  }
});

export default app;
