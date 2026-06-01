/**
 * P0 边缘 API 骨架：生产环境代理到 Container；本地可直连 PIPELINE_URL。
 */
import { Hono } from "hono";
import { cors } from "hono/cors";

type Bindings = {
  PIPELINE_URL: string;
  ALLOWED_ORIGINS: string;
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
      headers: upstream.headers,
    });
  } catch {
    return c.text("上游服务不可用", 502);
  }
});

export default app;
