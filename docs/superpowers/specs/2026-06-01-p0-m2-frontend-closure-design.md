# P0-M2 前端闭环 — 设计说明（Spec）

> **状态：** 已批准（基于 [p0-mvp-implementation.md](../../p0-mvp-implementation.md) §3、§6 Phase 2 与 `main` @ 0.2.0 差距分析）  
> **下一步：** [实施计划](../plans/2026-06-01-p0-m2-frontend-closure.md)（`writing-plans`）

## Goal

让浏览器端完成 P0 验收闭环（§1.2）：上传 DOCX + JD → 可理解等待 → 五段式结果 → 接受/拒绝/编辑 → 下载 DOCX；375px 可用。

## 非目标（本阶段不做）

- Cloudflare D1/R2/Cron、公网部署（工作包 B/C）
- 解析失败时粘贴全文简历（Phase 3）
- `matched` 带简历证据摘录（可后续 API 扩展）

## 架构

- **前端：** 将 `web/app/s/[id]/page.tsx` 拆为容器 + `web/components/*`；轮询 `GET /sessions/{id}` 不变。
- **后端小扩展：** `PATCH` 支持可选 `revised`；会话增加 `processing_step` 供等待 UI。
- **原则：** 复用现有 `export_guard` / PolicyGuard；不新增 `ChangeStatus.edited`（编辑后 `accepted` + 更新 `revised`）。

## 结果页信息顺序（§3.2）

1. JD 解读 → 2. 已匹配 → 匹配度条 → 3. 部分匹配 → 4. 缺失（含反编造提示）→ 5. 免费 3 条修改建议

## 关键 UX

| 项 | 决策 |
|----|------|
| 编辑 | 保存即 `accepted` + 写入 `revised` |
| 导出 | 仅 DOCX 文案；`format` 来自 API |
| 进度 | 后端 `processing_step` 枚举四步 |
| 隐私 | 不写死 24h 自动删（TTL 未上线） |

## 验证

- Server: `pytest` + 新 PATCH/export 用例
- Web: `npm run build`
- 人工: [p0-mvp-implementation.md §7.3](../../p0-mvp-implementation.md)
