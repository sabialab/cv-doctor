# P0-M2 Frontend Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the P0 browser loop (upload → stepped wait → §3.2 result layout → accept/reject/edit → DOCX export) on stub and real pipeline, mobile-friendly at 375px.

**Architecture:** Extend the existing FastAPI session API with optional `revised` on PATCH and `processing_step` on GET; refactor Next.js result page into focused components under `web/components/` while keeping polling on `GET /sessions/{id}`. No new `ChangeStatus` enum value—edit persists `revised` and sets `accepted`.

**Tech Stack:** FastAPI, Pydantic v2, pytest; Next.js 15 App Router, React 19, Tailwind 4, TypeScript.

**Spec:** [docs/superpowers/specs/2026-06-01-p0-m2-frontend-closure-design.md](../specs/2026-06-01-p0-m2-frontend-closure-design.md)

**Branch:** `feat/p0-m2-frontend-closure` from `origin/main`

**Plan revisions:** 2026-06-02 — P0 review fixes: PATCH `revised`/`status` exclusivity, export content assertion, `AnalysisProgress` done-state logic, retain `PolicyGuardBanner`, §3/§4 headings, `processing_steps` constants.

---

## File structure (locked)

| Path | Responsibility |
|------|----------------|
| `server/src/api/schemas.py` | `ChangePatchRequest.revised`, `SessionStatusResponse.processing_step`, `free_change_limit` in result |
| `server/src/services/session_store.py` | `processing_step` field; `patch_change(..., status=, revised=)` |
| `server/src/main.py` | Progress updates in `_run_diagnosis`; PATCH handler validation |
| `server/src/pipeline.py` | Optional `on_step(step)` callback between stages |
| `server/src/processing_steps.py` | Shared step id constants (`PARSING_RESUME`, …) |
| `server/tests/test_api_patch_change.py` | PATCH `revised` / `status` + export DOCX content |
| `server/tests/test_api_processing_step.py` | GET exposes steps during stub run |
| `web/lib/api.ts` | Types + `patchChange` body + `getSession` fields |
| `web/lib/constants.ts` | Step labels, `FREE_CHANGE_LIMIT = 3` |
| `web/components/AnalysisProgress.tsx` | Four-step wait UI |
| `web/components/DiffCard.tsx` | Accept / reject / edit + evidence |
| `web/components/JdSummarySection.tsx` | §1 JD |
| `web/components/MatchedSection.tsx` | §2 matched list |
| `web/components/MatchScoreBar.tsx` | Score after matched |
| `web/components/PartialGapSection.tsx` | §3 partial |
| `web/components/MissingGapSection.tsx` | §4 missing + anti-fabrication note |
| `web/components/ChangesSection.tsx` | §5 free 3 changes + export |
| `web/components/PolicyGuardBanner.tsx` | `policy_guard` warnings (preserve from current page) |
| `web/app/s/[id]/page.tsx` | Container: poll, errors, compose sections |
| `web/app/page.tsx` | Home copy (stub vs real, cloud model) |
| `web/app/privacy/page.tsx` | Aligned privacy copy |

---

### Task 1: PATCH change with optional `revised`

**PATCH contract (locked):**

| Body | Effect |
|------|--------|
| `{ "revised": "…" }` only | Update `revised`, set `status=accepted` |
| `{ "status": "accepted" \| "rejected" \| "pending" }` only | Update status only |
| Both `revised` and `status` | **422** — client must not send both (frontend: edit → `{ revised }`; accept/reject → `{ status }`) |

**Files:**
- Create: `server/tests/test_api_patch_change.py`
- Modify: `server/src/api/schemas.py`
- Modify: `server/src/services/session_store.py`
- Modify: `server/src/main.py`

- [ ] **Step 1: Write the failing tests**

Create `server/tests/test_api_patch_change.py`:

```python
"""PATCH /sessions/{id}/changes/{id} — status and revised text."""

from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from src.main import app


def _minimal_docx() -> bytes:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("负责后端开发与维护。")
    doc.add_paragraph("熟悉 Python")
    doc.save(buf)
    return buf.getvalue()


def _ready_session(client: TestClient) -> tuple[str, str, str]:
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}
    data = {"jd_text": "需要 Python 和 FastAPI 经验的后端工程师。"}
    sid = client.post("/sessions", files=files, data=data).json()["session_id"]
    body = client.get(f"/sessions/{sid}").json()
    ch0 = body["result"]["changes"][0]
    return sid, ch0["id"], ch0["original"]


def test_patch_revised_only_updates_export_docx():
    client = TestClient(app)
    sid, cid, original = _ready_session(client)
    edited = f"{original.rstrip('。')}（用户编辑稿）。"
    r = client.patch(f"/sessions/{sid}/changes/{cid}", json={"revised": edited})
    assert r.status_code == 200
    got = client.get(f"/sessions/{sid}").json()
    ch = next(c for c in got["result"]["changes"] if c["id"] == cid)
    assert ch["revised"] == edited
    assert ch["status"] == "accepted"
    exp = client.post(f"/sessions/{sid}/export")
    assert exp.status_code == 200
    down = client.get(exp.json()["download_url"])
    assert down.status_code == 200
    out = Document(BytesIO(down.content))
    blob = "\n".join(p.text for p in out.paragraphs)
    assert "用户编辑稿" in blob


def test_patch_rejects_revised_and_status_together():
    client = TestClient(app)
    sid, cid, _ = _ready_session(client)
    r = client.patch(
        f"/sessions/{sid}/changes/{cid}",
        json={"revised": "x", "status": "rejected"},
    )
    assert r.status_code == 422


def test_patch_status_only_reject():
    client = TestClient(app)
    sid, cid, _ = _ready_session(client)
    r = client.patch(f"/sessions/{sid}/changes/{cid}", json={"status": "rejected"})
    assert r.status_code == 200
    ch = next(
        c for c in client.get(f"/sessions/{sid}").json()["result"]["changes"] if c["id"] == cid
    )
    assert ch["status"] == "rejected"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd server && uv run pytest tests/test_api_patch_change.py -v`

Expected: FAIL (handler/store not updated yet)

- [ ] **Step 3: Implement schema + store + route**

In `server/src/api/schemas.py`, replace `ChangePatchRequest` with (merge into existing pydantic imports):

```python
class ChangePatchRequest(BaseModel):
    status: ChangeStatus | None = None
    revised: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_patch_body(self) -> "ChangePatchRequest":
        if self.status is None and self.revised is None:
            raise ValueError("status 或 revised 至少提供一项")
        if self.status is not None and self.revised is not None:
            raise ValueError("revised 与 status 不能同时提供")
        return self
```

In `server/src/services/session_store.py`, replace `patch_change` with:

```python
def patch_change(
    session_id: str,
    change_id: str,
    *,
    status: ChangeStatus | str | None = None,
    revised: str | None = None,
) -> SessionRecord | None:
    with _lock:
        rec = _sessions.get(session_id)
        if rec is None or rec.result is None:
            return None
        for ch in rec.result.changes:
            if ch.id != change_id:
                continue
            if revised is not None:
                ch.revised = revised.strip()
                ch.status = ChangeStatus.ACCEPTED
            elif status is not None:
                ch.status = ChangeStatus(status) if isinstance(status, str) else status
            return rec
        return None
```

In `server/src/main.py`, update the PATCH handler:

```python
@app.patch("/sessions/{session_id}/changes/{change_id}", response_model=ChangePatchResponse)
def patch_change_route(
    session_id: str, change_id: str, body: ChangePatchRequest
) -> ChangePatchResponse:
    rec = store_patch_change(
        session_id,
        change_id,
        status=body.status,
        revised=body.revised,
    )
    if rec is None:
        raise HTTPException(404, detail="会话、结果或修改项不存在")
    ch = next(c for c in rec.result.changes if c.id == change_id)
    return ChangePatchResponse(id=change_id, status=ch.status)
```

FastAPI returns **422** for `ChangePatchRequest` validation errors automatically.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd server && uv run pytest tests/test_api_patch_change.py -v`

Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add server/src/api/schemas.py server/src/services/session_store.py server/src/main.py server/tests/test_api_patch_change.py
git commit -m "feat(api): allow PATCH change revised text and accept for export"
```

---

### Task 2: `processing_step` on session GET

**Note:** `TestClient` runs the diagnosis background task synchronously, so integration tests will **not** observe step transitions. Step UI is validated in **Task 7 manual smoke (M2-2)** and optional Task 10 browser check.

**Files:**
- Create: `server/src/processing_steps.py`
- Create: `server/tests/test_api_processing_step.py`
- Modify: `server/src/services/session_store.py`
- Modify: `server/src/api/schemas.py`
- Modify: `server/src/main.py`
- Modify: `server/src/pipeline.py`

- [ ] **Step 1: Write the failing test**

Create `server/tests/test_api_processing_step.py`:

```python
from fastapi.testclient import TestClient

from src.main import app
from src.services import session_store


def test_get_session_includes_processing_step(monkeypatch):
    monkeypatch.setattr(session_store, "_sessions", {})
    rec = session_store.create_session(resume_bytes=b"x", jd_text="jd")
    session_store.update_session(
        rec.session_id, status="processing", processing_step="analyzing_jd"
    )
    client = TestClient(app)
    body = client.get(f"/sessions/{rec.session_id}").json()
    assert body["status"] == "processing"
    assert body["processing_step"] == "analyzing_jd"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_api_processing_step.py::test_get_session_includes_processing_step -v`

Expected: FAIL (`processing_step` missing or field rejected)

- [ ] **Step 3: Add constants, field, and wire progress**

Create `server/src/processing_steps.py`:

```python
PARSING_RESUME = "parsing_resume"
ANALYZING_JD = "analyzing_jd"
MATCHING = "matching"
GENERATING_CHANGES = "generating_changes"

STUB_PROGRESS_SEQUENCE = (
    PARSING_RESUME,
    ANALYZING_JD,
    MATCHING,
    GENERATING_CHANGES,
)
```

Add to `SessionRecord` in `session_store.py`:

```python
processing_step: str | None = None
```

In `schemas.py` `SessionStatusResponse`:

```python
processing_step: str | None = None
```

In `get_session_route` (`main.py`):

```python
return SessionStatusResponse(
    session_id=rec.session_id,
    status=rec.status,
    result=api_result,
    error=rec.error,
    processing_step=rec.processing_step,
)
```

Add helper in `main.py`:

```python
def _progress(session_id: str, step: str) -> None:
    update_session(session_id, processing_step=step)
```

Stub branch in `_run_diagnosis` (import `STUB_PROGRESS_SEQUENCE` from `processing_steps`):

```python
from src.processing_steps import PARSING_RESUME, STUB_PROGRESS_SEQUENCE

update_session(session_id, status="processing", processing_step=PARSING_RESUME)
for step in STUB_PROGRESS_SEQUENCE[1:]:
    _progress(session_id, step)
# then build_stub_diagnosis() + apply_policy_guard as today
update_session(session_id, status="ready", result=result, error=None, processing_step=None)
```

Real pipeline: add optional parameter to `run_diagnosis` in `pipeline.py`:

```python
from collections.abc import Callable

def run_diagnosis(
    resume_bytes: bytes,
    jd_text: str,
    *,
    llm: LLMClient | None = None,
    on_step: Callable[[str], None] | None = None,
) -> DiagnosisResult:
    def step(name: str) -> None:
        if on_step:
            on_step(name)

    step("parsing_resume")
    resume = parse_resume(resume_bytes)
    step("analyzing_jd")
    jd = parse_jd(jd_text, client)
    step("matching")
    evidence = build_evidence_store(resume, jd)
    gap = analyze_gaps(resume, jd)
    step("generating_changes")
    change_set = generate_changes(resume, jd, gap, evidence, client, max_changes=3)
    ...
```

Call from `main.py`:

```python
result = run_diagnosis(
    rec.resume_bytes,
    rec.jd_text,
    on_step=lambda s: _progress(session_id, s),
)
```

- [ ] **Step 4: Run tests**

Run: `cd server && uv run pytest tests/test_api_processing_step.py tests/test_api.py -q`

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add server/src/processing_steps.py server/src/services/session_store.py server/src/api/schemas.py server/src/main.py server/src/pipeline.py server/tests/test_api_processing_step.py
git commit -m "feat(api): expose processing_step during diagnosis"
```

---

### Task 3: API `free_change_limit` in diagnosis result

**Files:**
- Modify: `server/src/api/schemas.py`
- Modify: `server/tests/test_api.py`

- [ ] **Step 1: Extend failing assertion in test_api**

In `test_session_flow_stub`, after loading result, add:

```python
assert body["result"].get("free_change_limit") == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_api.py::test_session_flow_stub -v`

Expected: FAIL (`free_change_limit` missing)

- [ ] **Step 3: Add field in diagnosis_result_for_api**

At end of returned dict in `diagnosis_result_for_api`:

```python
"free_change_limit": 3,
```

- [ ] **Step 4: Run test**

Run: `cd server && uv run pytest tests/test_api.py::test_session_flow_stub -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add server/src/api/schemas.py server/tests/test_api.py
git commit -m "feat(api): return free_change_limit in diagnosis result"
```

---

### Task 4: Web API client + constants

**Files:**
- Create: `web/lib/constants.ts`
- Modify: `web/lib/api.ts`

- [ ] **Step 1: Create constants**

Create `web/lib/constants.ts`:

```typescript
export const FREE_CHANGE_LIMIT = 3;

export const PROCESSING_STEPS = [
  { id: "parsing_resume", label: "解析简历" },
  { id: "analyzing_jd", label: "分析岗位描述" },
  { id: "matching", label: "匹配与缺口" },
  { id: "generating_changes", label: "生成修改建议" },
] as const;

export type ProcessingStepId = (typeof PROCESSING_STEPS)[number]["id"];
```

- [ ] **Step 2: Update api.ts types and patchChange**

Add to `getSession` return type: `processing_step?: string | null`

Add to `DiagnosisResult`: `free_change_limit?: number`

Change `patchChange`:

```typescript
export async function patchChange(
  sessionId: string,
  changeId: string,
  body: { status?: "accepted" | "rejected" | "pending"; revised?: string },
): Promise<void> {
  const res = await fetch(apiUrl(`/sessions/${sessionId}/changes/${changeId}`), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || "更新失败");
  }
}

export async function exportSession(
  sessionId: string,
): Promise<{ download_url: string; format: "docx" | "txt" }> {
```

- [ ] **Step 3: Verify TypeScript**

Run: `cd web && npm run build`

Expected: exit 0 (may fail until components updated—fix imports in Task 7)

- [ ] **Step 4: Commit**

```bash
git add web/lib/constants.ts web/lib/api.ts
git commit -m "feat(web): api client for revised patch and processing_step"
```

---

### Task 5: `AnalysisProgress` + `DiffCard` components

**Files:**
- Create: `web/components/AnalysisProgress.tsx`
- Create: `web/components/DiffCard.tsx`

- [ ] **Step 1: Create AnalysisProgress**

Create `web/components/AnalysisProgress.tsx` (only rendered while `status` is `pending`/`processing` — see Task 7):

```tsx
"use client";

import { PROCESSING_STEPS } from "@/lib/constants";

export function AnalysisProgress({ currentStep }: { currentStep?: string | null }) {
  const activeIndex =
    currentStep == null || currentStep === ""
      ? -1
      : PROCESSING_STEPS.findIndex((s) => s.id === currentStep);

  return (
    <ol className="mt-4 space-y-2 text-sm" aria-label="分析进度">
      {PROCESSING_STEPS.map((step, i) => {
        const done = activeIndex >= 0 && i < activeIndex;
        const active = activeIndex >= 0 && i === activeIndex;
        return (
          <li
            key={step.id}
            className={
              active
                ? "font-medium text-neutral-900"
                : done
                  ? "text-neutral-500"
                  : "text-neutral-400"
            }
          >
            {i + 1}. {step.label}
            {active ? " …" : done ? " ✓" : ""}
          </li>
        );
      })}
    </ol>
  );
}
```

- [ ] **Step 2: Create DiffCard**

Create `web/components/DiffCard.tsx` with props:

```typescript
export type DiffCardProps = {
  index: number;
  total: number;
  change: DiagnosisResult["changes"][number];
  confirmAcceptId: string | null;
  onAccept: (id: string, confirmed?: boolean) => void;
  onReject: (id: string) => void;
  onSaveEdit: (id: string, revised: string) => Promise<void>;
  onCancelConfirm: () => void;
};
```

Implement: title `建议 {index}/{total}`; show `source_label` + `evidence_ids.join(", ")` under「依据」; edit mode with `<textarea>` prefilled `revised`; buttons 保存并采纳 / 取消 / 采纳 / 拒绝; reuse existing risk gate (`high` or `requires_user_confirmation`); `min-h-[44px]` on buttons.

`onSaveEdit` calls `patchChange(sessionId, id, { revised })` only (no `status` — API forbids both).

- [ ] **Step 3: Build**

Run: `cd web && npm run build`

Expected: PASS once page imports exist (Task 7); or compile components only with `tsc --noEmit` if page not wired yet

- [ ] **Step 4: Commit**

```bash
git add web/components/AnalysisProgress.tsx web/components/DiffCard.tsx
git commit -m "feat(web): AnalysisProgress and DiffCard components"
```

---

### Task 6: Result page section components

**Files:**
- Create: `web/components/JdSummarySection.tsx`
- Create: `web/components/MatchedSection.tsx`
- Create: `web/components/MatchScoreBar.tsx`
- Create: `web/components/PartialGapSection.tsx`
- Create: `web/components/MissingGapSection.tsx`
- Create: `web/components/ChangesSection.tsx`
- Create: `web/components/PolicyGuardBanner.tsx`

- [ ] **Step 1: Implement sections (order per spec)**

**Out of scope for M2:** `gap_report.keyword_missing`, `responsibility_gaps` (no new UI; avoid scope creep).

`JdSummarySection` — props: `jd: DiagnosisResult["jd_interpretation"]`; heading「1. 岗位在招什么人」; `role_summary` + lists.

`MatchedSection` — props: `matched: string[]`; heading「2. 你已匹配」; green cards; hide if empty.

`MatchScoreBar` — props: `match_score`; subline after §2; large `overall / 100` (not first visual on page).

`PartialGapSection` — heading「3. 部分匹配」; `partial_match` items; hide section if empty.

`MissingGapSection` — heading「4. 缺失项」; `hard_missing` + `preferred_missing`; top note:

```tsx
<p className="text-sm text-neutral-600">
  以下缺口不会自动写入简历，仅作待补充建议（请勿编造经历）。
</p>
```

`ChangesSection` — heading「5. 简历手术建议（免费 3 条）」; maps `changes` to `DiffCard`; export button:

```tsx
<button type="button" onClick={onExport} className="mt-4 ...">
  导出已采纳修改为 Word（.docx）
</button>
```

Download link when `exportLink` set:

```tsx
<a href={exportLink} download="resume-export.docx" className="...">
  下载 Word 文档
</a>
```

`PolicyGuardBanner` — props: `policy_guard` from result; amber box when `!passed && warnings.length`; same copy as current `page.tsx` compliance block.

- [ ] **Step 2: Build**

Run: `cd web && npm run build`

Expected: PASS after Task 7 wires imports

- [ ] **Step 3: Commit**

```bash
git add web/components/JdSummarySection.tsx web/components/MatchedSection.tsx web/components/MatchScoreBar.tsx web/components/PartialGapSection.tsx web/components/MissingGapSection.tsx web/components/ChangesSection.tsx web/components/PolicyGuardBanner.tsx
git commit -m "feat(web): result page section components per P0 IA"
```

---

### Task 7: Refactor `web/app/s/[id]/page.tsx`

**Files:**
- Modify: `web/app/s/[id]/page.tsx`

- [ ] **Step 1: Replace monolith with container**

- State: `processingStep` from `getSession().processing_step`.
- **Progress UI:** render `<AnalysisProgress />` **only when** `status === "pending" || status === "processing"` (never on `ready`/`failed`).
- If `stillAnalyzing && !result`: show progress +「正在分析简历与岗位描述…」; optional: after 30s polling show「仍在分析，请稍候」.
- Ready layout order: `JdSummarySection` → `MatchedSection` → `MatchScoreBar` → `PolicyGuardBanner` (if warnings) → `PartialGapSection` → `MissingGapSection` → `ChangesSection`.
- `onSaveEdit`: `await patchChange(sessionId, id, { revised }); await load();` — **do not** send `status` with `revised`.
- `onAccept` / `onReject`: `patchChange(..., { status: "accepted" })` or `{ status: "rejected" }` only.
- `onExport`: use `format` from `exportSession`; download link `download="resume-export.docx"`.
- Remove all「文本稿」「.txt 桩」strings.

- [ ] **Step 2: Build**

Run: `cd web && npm run build`

Expected: PASS

- [ ] **Step 3: Manual stub smoke (M2-2 — required)**

Run server + web per README; upload `docs/fixtures/sample-resume.docx` + paste JD.

Checklist:

- [ ] Four progress labels appear and advance (browser; not visible in pytest).
- [ ] Section headings 1–5 in correct order.
- [ ] Edit one change → export DOCX → open file → edited phrase present.
- [ ] Delete session works.

- [ ] **Step 4: Commit**

```bash
git add web/app/s/[id]/page.tsx
git commit -m "feat(web): M2 result page layout, progress, edit, docx export UI"
```

---

### Task 8: Home and privacy copy

**Files:**
- Modify: `web/app/page.tsx`
- Modify: `web/app/privacy/page.tsx`

- [ ] **Step 1: Update home subtitle**

Replace stub-only line with:

```tsx
<p className="mt-2 text-neutral-600">
  上传简历（DOCX）并粘贴岗位描述，获取匹配诊断与可审阅的修改建议。本地默认联调模式；配置
  USE_REAL_PIPELINE=1 与 DEEPSEEK_API_KEY 后启用真实分析（见 server/.env.example）。
</p>
```

Privacy footer: mention third-party cloud model (DeepSeek); do **not** claim 24h auto-delete—keep「结果页可手动删除」.

- [ ] **Step 2: Align privacy page**

Match home promises; note production will use R2/D1 (planned).

- [ ] **Step 3: Build**

Run: `cd web && npm run build`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add web/app/page.tsx web/app/privacy/page.tsx
git commit -m "docs(web): home and privacy copy for stub vs real pipeline"
```

---

### Task 9: Mobile 375px pass

**Files:**
- Modify: `web/app/globals.css` (if needed)
- Modify: `web/components/DiffCard.tsx` (collapse long text)

- [ ] **Step 1: Add collapsible long originals**

In `DiffCard`, wrap `original` / `revised` in `<details>` when length &gt; 120 chars.

- [ ] **Step 2: Global overflow**

In `web/app/layout.tsx` or `globals.css`:

```css
main {
  overflow-x: hidden;
}
```

Ensure textarea `text-base` (16px) on home JD field.

- [ ] **Step 3: Verify**

Run: `cd web && npm run build`

Chrome DevTools iPhone SE 375px: no horizontal scroll; tap targets ≥44px.

- [ ] **Step 4: Commit**

```bash
git add web/components/DiffCard.tsx web/app/globals.css web/app/page.tsx
git commit -m "fix(web): mobile 375px layout and collapsible diff text"
```

---

### Task 10: Full verification (REQUIRED SUB-SKILL: verification-before-completion)

**Files:** none (commands only)

- [ ] **Step 1: Server CI parity**

```bash
cd server && uv sync --extra dev --frozen && uv run ruff check src/main.py src/api/ src/services/session_store.py src/pipeline.py && uv run pytest -q
```

Expected: All checks passed; 42+ tests pass

- [ ] **Step 2: Web + worker**

```bash
cd web && npm ci && npm run build
cd ../worker && npm ci && npm run typecheck
```

Expected: exit 0

- [ ] **Step 3: PR checklist**

Manual: [p0-mvp-implementation.md §7.3](../../p0-mvp-implementation.md) — Chinese JD, no fabricated export, DOCX opens, delete session.

Optional (local): `USE_REAL_PIPELINE=1` + `DEEPSEEK_API_KEY` + fixture resume/JD — one full browser pass.

- [ ] **Step 4: CodeRabbit before push**

```bash
cr review --base main --plain
```

Expected: P1/P2 = 0

---

## Spec coverage (self-review)

| Spec requirement | Task |
|------------------|------|
| Edit + export revised | Task 1, 5, 7 |
| PATCH body rules (exclusive) | Task 1, 4, 7 |
| processing_step UI | Task 2, 4, 5, 7 (+ Task 7 manual M2-2) |
| §3.2 section order (1–5 headings) | Task 6, 7 |
| Policy guard warnings | Task 6, 7 |
| Free 3 changes | Task 3, 6 |
| DOCX export copy + content | Task 1, 6, 7 |
| Home/privacy | Task 8 |
| 375px | Task 9 |
| Out of scope (D1/R2, keyword_missing UI) | — |

---

## Review checklist (post-amendment)

- [x] P0-1: `revised` / `status` mutually exclusive + tests
- [x] P0-2: export DOCX content assertion in Task 1
- [x] P0-3: `AnalysisProgress` done logic + render only while processing
- [x] P0-4: `PolicyGuardBanner` preserved in Task 6/7

---

## PR

- One PR: `feat/p0-m2-frontend-closure` → `main`
- Squash merge; then `checkout main`, `pull`, delete feature branch (see `pr-workflow.mdc`)
