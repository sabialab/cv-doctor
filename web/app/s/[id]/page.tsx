"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { AnalysisProgress } from "@/components/AnalysisProgress";
import { ChangesSection } from "@/components/ChangesSection";
import { JdSummarySection } from "@/components/JdSummarySection";
import { MatchedSection } from "@/components/MatchedSection";
import { MatchScoreBar } from "@/components/MatchScoreBar";
import { MissingGapSection } from "@/components/MissingGapSection";
import { PartialGapSection } from "@/components/PartialGapSection";
import { PolicyGuardBanner } from "@/components/PolicyGuardBanner";
import {
  deleteSession,
  exportDownloadUrl,
  exportSession,
  getSession,
  isResumeParseError,
  patchChange,
  type DiagnosisResult,
  type SessionStatus,
} from "@/lib/api";

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  const [status, setStatus] = useState<SessionStatus>("pending");
  const [processingStep, setProcessingStep] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [exportLink, setExportLink] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [confirmAcceptId, setConfirmAcceptId] = useState<string | null>(null);
  const [pollSlow, setPollSlow] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await getSession(sessionId);
      setStatus(data.status);
      setProcessingStep(data.processing_step ?? null);
      setResult(data.result);
      setError(data.error);
    } catch (e) {
      setStatus("failed");
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoaded(true);
    }
  }, [sessionId]);

  useEffect(() => {
    load();
    if (status === "pending" || status === "processing") {
      const t = setInterval(load, 1500);
      return () => clearInterval(t);
    }
  }, [load, status]);

  useEffect(() => {
    if (status !== "pending" && status !== "processing") {
      setPollSlow(false);
      return;
    }
    const slow = setTimeout(() => setPollSlow(true), 30_000);
    return () => clearTimeout(slow);
  }, [status]);

  const stillAnalyzing = status === "pending" || status === "processing";

  async function onAccept(changeId: string, confirmed = false) {
    const change = result?.changes.find((c) => c.id === changeId);
    const needsGate =
      change && (change.risk_level === "high" || change.requires_user_confirmation);
    if (needsGate && !confirmed) {
      setConfirmAcceptId(changeId);
      return;
    }
    setConfirmAcceptId(null);
    setActionError(null);
    setExportLink(null);
    try {
      await patchChange(sessionId, changeId, { status: "accepted" });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "采纳失败");
    }
  }

  async function onReject(changeId: string) {
    setConfirmAcceptId(null);
    setActionError(null);
    setExportLink(null);
    try {
      await patchChange(sessionId, changeId, { status: "rejected" });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "拒绝失败");
    }
  }

  async function onSaveEdit(changeId: string, revised: string) {
    setActionError(null);
    setExportLink(null);
    try {
      await patchChange(sessionId, changeId, { revised });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "保存失败");
      throw e;
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

  if (!loaded) {
    return (
      <main className="mx-auto max-w-2xl overflow-x-hidden px-4 py-12">
        <p className="text-neutral-600">加载中…</p>
      </main>
    );
  }

  if (stillAnalyzing && !result) {
    return (
      <main className="mx-auto max-w-2xl overflow-x-hidden px-4 py-12">
        <h1 className="text-xl font-semibold">正在分析</h1>
        <p className="mt-2 text-neutral-600">正在分析简历与岗位描述…</p>
        <AnalysisProgress currentStep={processingStep} />
        {pollSlow && (
          <p className="mt-4 text-sm text-amber-800">仍在分析，请稍候（页面将自动刷新）</p>
        )}
      </main>
    );
  }

  if (status === "failed" || !result) {
    const parseHint = error && isResumeParseError(error);
    return (
      <main className="mx-auto max-w-2xl overflow-x-hidden px-4 py-12">
        <p className="text-red-600">{error || "分析失败"}</p>
        {parseHint && (
          <p className="mt-3 text-sm text-amber-900">
            可{" "}
            <Link href="/?paste=1" className="underline">
              返回首页粘贴简历全文
            </Link>{" "}
            后重新诊断（无需再上传 Word 文件）。
          </p>
        )}
        <Link href="/" className="mt-4 inline-block text-sm underline">
          返回首页
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl space-y-10 overflow-x-hidden px-4 py-10">
      {stillAnalyzing && (
        <div className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-900">
          <p>分析进行中，页面将自动刷新…</p>
          <AnalysisProgress currentStep={processingStep} />
        </div>
      )}
      {actionError && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{actionError}</p>
      )}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">诊断结果</h1>
        <div className="flex flex-wrap gap-3 text-sm">
          <Link href="/" className="min-h-[44px] leading-[44px] text-neutral-600 underline">
            新诊断
          </Link>
          <button
            type="button"
            onClick={onDelete}
            disabled={deleting}
            className="min-h-[44px] text-red-700 underline disabled:opacity-50"
          >
            {deleting ? "删除中…" : "删除本会话"}
          </button>
        </div>
      </div>

      <JdSummarySection jd={result.jd_interpretation} />
      <MatchedSection matched={result.gap_report.matched} />
      <MatchScoreBar matchScore={result.match_score} />
      {result.policy_guard && <PolicyGuardBanner policyGuard={result.policy_guard} />}
      <PartialGapSection items={result.gap_report.partial_match} />
      <MissingGapSection
        hardMissing={result.gap_report.hard_missing}
        preferredMissing={result.gap_report.preferred_missing}
      />
      <ChangesSection
        changes={result.changes}
        freeLimit={result.free_change_limit}
        confirmAcceptId={confirmAcceptId}
        exportLink={exportLink}
        onExport={onExport}
        onAccept={onAccept}
        onReject={onReject}
        onSaveEdit={onSaveEdit}
        onCancelConfirm={() => setConfirmAcceptId(null)}
      />
    </main>
  );
}
