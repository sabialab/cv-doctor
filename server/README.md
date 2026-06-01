# CV Doctor — Python 流水线

P0：FastAPI 会话 API + 桩诊断流水线。生产部署见仓库根目录 `docs/p0-cloudflare-stack.md`（Cloudflare Container）。

```bash
uv sync
cp .env.example .env
uv run uvicorn src.main:app --reload --port 8787
```
