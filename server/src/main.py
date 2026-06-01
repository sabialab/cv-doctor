"""P0 FastAPI — 本地开发与 Cloudflare Container 入口。"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.api.schemas import (
    ChangePatchRequest,
    ChangePatchResponse,
    ExportResponse,
    PrivacyResponse,
    SessionCreateResponse,
    SessionStatusResponse,
    diagnosis_result_for_api,
)
from src.config import config
from src.models import ChangeStatus
from src.services.export_guard import exportable_changes
from src.services.exporter_docx import apply_changes_to_docx
from src.services.policy_guard import apply_policy_guard
from src.services.session_store import (
    create_session,
    delete_session,
    get_session,
    update_session,
)
from src.services.session_store import (
    patch_change as store_patch_change,
)
from src.services.stub_pipeline import build_stub_diagnosis

app = FastAPI(title="CV Doctor API", version="0.1.0-p0")

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXPORT_DIR = Path(os.getenv("STORAGE_PATH", "./uploads")) / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _run_diagnosis(session_id: str) -> None:
    rec = get_session(session_id)
    if rec is None:
        return
    update_session(session_id, status="processing")
    try:
        if config.use_real_pipeline:
            from src.pipeline import run_diagnosis

            result = run_diagnosis(rec.resume_bytes, rec.jd_text)
        else:
            result = build_stub_diagnosis()
            filtered, summary = apply_policy_guard(result.changes)
            result = result.model_copy(
                update={"changes": filtered, "policy_guard": summary}
            )
        update_session(session_id, status="ready", result=result, error=None)
    except Exception as exc:  # noqa: BLE001 — P0 边界
        update_session(session_id, status="failed", error=str(exc))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionCreateResponse)
async def create_session_route(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    jd_text: str = Form(""),
) -> SessionCreateResponse:
    if not resume.filename or not resume.filename.lower().endswith(".docx"):
        raise HTTPException(400, detail="仅支持 .docx 简历")
    if not jd_text.strip():
        raise HTTPException(400, detail="请粘贴岗位描述")

    data = await resume.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, detail="文件超过 10MB")

    record = create_session(resume_bytes=data, jd_text=jd_text.strip())
    background_tasks.add_task(_run_diagnosis, record.session_id)
    return SessionCreateResponse(session_id=record.session_id, status=record.status)


@app.get("/sessions/{session_id}", response_model=SessionStatusResponse)
def get_session_route(session_id: str) -> SessionStatusResponse:
    rec = get_session(session_id)
    if rec is None:
        raise HTTPException(404, detail="会话不存在或已过期")
    api_result = diagnosis_result_for_api(rec.result) if rec.result else None
    return SessionStatusResponse(
        session_id=rec.session_id,
        status=rec.status,
        result=api_result,
        error=rec.error,
    )


@app.patch("/sessions/{session_id}/changes/{change_id}", response_model=ChangePatchResponse)
def patch_change(session_id: str, change_id: str, body: ChangePatchRequest) -> ChangePatchResponse:
    rec = store_patch_change(session_id, change_id, body.status)
    if rec is None:
        raise HTTPException(404, detail="会话、结果或修改项不存在")
    return ChangePatchResponse(id=change_id, status=body.status)


@app.post("/sessions/{session_id}/export", response_model=ExportResponse)
def export_session(session_id: str) -> ExportResponse:
    rec = get_session(session_id)
    if rec is None or rec.result is None:
        raise HTTPException(404, detail="会话不可用")

    to_export = exportable_changes(rec.result.changes)
    if not to_export:
        accepted_any = any(c.status == ChangeStatus.ACCEPTED for c in rec.result.changes)
        if accepted_any:
            raise HTTPException(
                400,
                detail="高风险修改不能导出；请仅接受低/中风险建议，或取消高风险项的接受",
            )
        raise HTTPException(400, detail="请先接受至少一条可导出的修改建议")

    out = EXPORT_DIR / f"{session_id}.docx"
    applied = apply_changes_to_docx(rec.resume_bytes, to_export, out)
    if applied == 0:
        raise HTTPException(
            400,
            detail="未在简历中找到可替换的原文片段，请编辑修改建议或重新上传简历",
        )
    update_session(session_id, export_path=str(out))
    return ExportResponse(
        download_url=f"/sessions/{session_id}/export/download",
        format="docx",
    )


@app.get("/sessions/{session_id}/export/download")
def download_export(session_id: str):
    rec = get_session(session_id)
    if rec is None or not rec.export_path or not Path(rec.export_path).is_file():
        raise HTTPException(404, detail="导出文件不存在")
    return FileResponse(
        rec.export_path,
        filename="resume-export.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.delete("/sessions/{session_id}", response_model=PrivacyResponse)
def delete_session_route(session_id: str) -> PrivacyResponse:
    rec = get_session(session_id)
    if rec is None:
        raise HTTPException(404, detail="会话不存在")
    if rec.export_path:
        Path(rec.export_path).unlink(missing_ok=True)
    delete_session(session_id)
    return PrivacyResponse(message="已删除")


@app.get("/privacy", response_model=PrivacyResponse)
def privacy_ack() -> PrivacyResponse:
    return PrivacyResponse(message="ok")
