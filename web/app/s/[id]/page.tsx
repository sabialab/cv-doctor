"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import {
  deleteSession,
  exportDownloadUrl,
  exportSession,
  getSession,
  patchChange,
  type DiagnosisResult,
  type SessionStatus,
} from "@/lib/api";

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  const [status, setStatus] = useState<SessionStatus>("pending");
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [exportLink, setExportLink] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [confirmAcceptId, setConfirmAcceptId] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getSession(sessionId);
      setStatus(data.status);
      setResult(data.result);
      setError(data.error);
    } catch (e) {
      setStatus("failed");
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [sessionId]);

  useEffect(() => {
    load();
    if (status === "pending" || status === "processing") {
      const t = setInterval(load, 1500);
      return () => clearInterval(t);
    }
  }, [load, status]);

  const stillAnalyzing = status === "pending" || status === "processing";

  async function onAccept(changeId: string, confirmed = false) {
    const change = result?.changes.find((c) => c.id === changeId);
    const needsGate =
      change &&
      (change.risk_level === "high" || change.requires_user_confirmation);
    if (needsGate && !confirmed) {
      setConfirmAcceptId(changeId);
      return;
    }
    setConfirmAcceptId(null);
    setActionError(null);
    try {
      await patchChange(sessionId, changeId, "accepted");
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "采纳失败");
    }
  }

  async function onReject(changeId: string) {
    setConfirmAcceptId(null);
    setActionError(null);
    try {
      await patchChange(sessionId, changeId, "rejected");
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "拒绝失败");
    }
  }

  async function onExport() {
    setActionError(null);
    try {
      const { download_url } = await exportSession(sessionId);
      setExportLink(exportDownloadUrl(sessionId, download_url));
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "导出失败");
    }
  }

  async function onDelete() {
    setDeleting(true);
    setActionError(null);
    try {
      await deleteSession(sessionId);
      router.push("/");
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "删除失败");
    } finally {
      setDeleting(false);
    }
  }

  if (stillAnalyzing && !result) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-neutral-600">正在分析简历与岗位描述…</p>
      </main>
    );
  }

  if (status === "failed" || !result) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-red-600">{error || "分析失败"}</p>
        <Link href="/" className="mt-4 inline-block text-sm underline">
          返回首页
        </Link>
      </main>
    );
  }

  const jd = result.jd_interpretation;
  const ms = result.match_score;
  const pg = result.policy_guard;

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 space-y-10">
      {stillAnalyzing && (
        <p className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-900">
          分析进行中，页面将自动刷新…
        </p>
      )}
      {actionError && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{actionError}</p>
      )}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">诊断结果</h1>
        <div className="flex gap-3 text-sm">
          <Link href="/" className="text-neutral-600 underline">
            新诊断
          </Link>
          <button
            type="button"
            onClick={onDelete}
            disabled={deleting}
            className="text-red-700 underline disabled:opacity-50"
          >
            {deleting ? "删除中…" : "删除本会话"}
          </button>
        </div>
      </div>

      <section className="rounded-xl border border-neutral-200 p-5">
        <h2 className="text-lg font-medium">1. 岗位解读</h2>
        <p className="mt-2 text-sm text-neutral-700">{jd.role_summary}</p>
        <ul className="mt-3 list-disc pl-5 text-sm text-neutral-600 space-y-1">
          {jd.hard_requirements.map((r, i) => (
            <li key={`hard-${i}`}>硬性：{r}</li>
          ))}
          {jd.preferred_requirements.map((r, i) => (
            <li key={`pref-${i}`}>优先：{r}</li>
          ))}
          {jd.responsibilities.map((r, i) => (
            <li key={`resp-${i}`}>职责：{r}</li>
          ))}
        </ul>
      </section>

      {pg && !pg.passed && pg.warnings.length > 0 && (
        <section className="rounded-xl border border-amber-200 bg-amber-50 p-5">
          <h2 className="text-lg font-medium">合规提示</h2>
          <ul className="mt-2 list-disc pl-5 text-sm text-amber-900 space-y-1">
            {pg.warnings.map((w, i) => (
              <li key={`pg-${i}`}>{w}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="rounded-xl border border-neutral-200 p-5">
        <h2 className="text-lg font-medium">2. 匹配度</h2>
        <p className="mt-2 text-3xl font-semibold">{ms.overall} / 100</p>
        <p className="text-sm text-neutral-500">状态：{ms.status}</p>
      </section>

      <section className="rounded-xl border border-neutral-200 p-5">
        <h2 className="text-lg font-medium">3. 缺口</h2>
        <p className="mt-2 text-sm">共 {result.gap_report.total_gaps} 项</p>
        <ul className="mt-2 space-y-2 text-sm">
          {result.gap_report.hard_missing.map((g, i) => (
            <li key={`hm-${i}`} className="rounded bg-red-50 p-2">
              <strong>{g.requirement}</strong> — {g.suggestion}
            </li>
          ))}
          {result.gap_report.preferred_missing.map((g, i) => (
            <li key={`pm-${i}`} className="rounded bg-amber-50 p-2">
              {g.requirement} — {g.suggestion}
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-xl border border-neutral-200 p-5">
        <h2 className="text-lg font-medium">4. 修改建议</h2>
        <div className="mt-4 space-y-4">
          {result.changes.map((ch) => (
            <div key={ch.id} className="rounded-lg bg-neutral-50 p-4 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-neutral-500">{ch.section}</p>
                {(ch.risk_level === "medium" || ch.risk_level === "high") && (
                  <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-900">
                    风险：{ch.risk_level}
                    {ch.requires_user_confirmation ? "（建议确认）" : ""}
                  </span>
                )}
              </div>
              <p className="mt-2 line-through text-neutral-500">{ch.original}</p>
              <p className="mt-1 font-medium text-green-800">{ch.revised}</p>
              <p className="mt-2 text-neutral-600">{ch.reason}</p>
              <p className="mt-1 text-xs text-neutral-400">{ch.source_label}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {confirmAcceptId === ch.id ? (
                  <>
                    <p className="w-full text-xs text-amber-900">
                      此为高风险修改，请确认内容属实后再采纳。
                    </p>
                    <button
                      type="button"
                      onClick={() => onAccept(ch.id, true)}
                      className="min-h-[44px] rounded bg-green-700 px-3 py-2 text-xs text-white"
                    >
                      确认采纳
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmAcceptId(null)}
                      className="min-h-[44px] rounded border border-neutral-300 px-3 py-2 text-xs"
                    >
                      取消
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => onAccept(ch.id)}
                      className="min-h-[44px] rounded bg-green-700 px-3 py-2 text-xs text-white"
                    >
                      采纳 {ch.status === "accepted" ? "✓" : ""}
                    </button>
                    <button
                      type="button"
                      onClick={() => onReject(ch.id)}
                      className="min-h-[44px] rounded border border-neutral-300 px-3 py-2 text-xs"
                    >
                      拒绝
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={onExport}
          className="mt-4 rounded-lg border border-neutral-900 px-4 py-2 text-sm"
        >
          导出已采纳修改（文本稿）
        </button>
        {exportLink && (
          <a href={exportLink} className="mt-2 block text-sm text-blue-700 underline">
            下载文本导出（.txt，P0 桩）
          </a>
        )}
      </section>
    </main>
  );
}
