"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { createSession, isResumeParseError } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [showPasteFallback, setShowPasteFallback] = useState(false);
  const [usePasteOnly, setUsePasteOnly] = useState(false);
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("paste") === "1") {
      setShowPasteFallback(true);
      setUsePasteOnly(true);
    }
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!consent) {
      setError("请先勾选同意隐私说明");
      return;
    }
    if (!jdText.trim()) {
      setError("请粘贴岗位描述");
      return;
    }

    const pasted = resumeText.trim();
    const sendingFile = !usePasteOnly && file;
    if (!sendingFile && !pasted) {
      setError("请上传 .docx 或粘贴简历全文");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const { session_id } = await createSession({
        jdText: jdText.trim(),
        consent,
        resume: sendingFile ? file : null,
        resumeText: pasted || undefined,
      });
      router.push(`/s/${session_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "提交失败";
      setError(message);
      if (isResumeParseError(message)) {
        setShowPasteFallback(true);
        setUsePasteOnly(true);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">CV Doctor</h1>
      <p className="mt-2 text-neutral-600">
        上传简历（DOCX）或粘贴简历全文，并填写岗位描述，获取匹配诊断与可审阅的修改建议。本地默认联调模式；配置
        USE_REAL_PIPELINE=1 与 DEEPSEEK_API_KEY 后启用真实分析（见 server/.env.example）。
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-6">
        <div>
          <label htmlFor="resume-file" className="block text-sm font-medium">
            简历（.docx，可选若下方已粘贴全文）
          </label>
          <input
            id="resume-file"
            type="file"
            accept=".docx"
            className="mt-1 block w-full text-sm"
            disabled={usePasteOnly}
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              if (e.target.files?.[0]) {
                setUsePasteOnly(false);
              }
            }}
          />
        </div>

        {(showPasteFallback || usePasteOnly) && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm text-amber-900">
              {showPasteFallback
                ? "无法从 Word 文件解析内容时，请粘贴简历全文后重试（无需重新上传文件）。"
                : "也可直接粘贴简历全文，无需上传文件。"}
            </p>
            <label htmlFor="resume-text" className="mt-3 block text-sm font-medium">
              简历全文（粘贴）
            </label>
            <textarea
              id="resume-text"
              className="mt-1 h-48 w-full rounded-lg border border-amber-300 bg-white p-3 text-base"
              placeholder="粘贴简历全文…"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
            {!usePasteOnly && (
              <button
                type="button"
                className="mt-2 text-sm text-amber-900 underline"
                onClick={() => {
                  setUsePasteOnly(true);
                  setFile(null);
                }}
              >
                仅使用粘贴内容，忽略已选文件
              </button>
            )}
          </div>
        )}

        {!showPasteFallback && !usePasteOnly && (
          <button
            type="button"
            className="text-sm text-neutral-600 underline"
            onClick={() => setShowPasteFallback(true)}
          >
            无法上传 DOCX？粘贴简历全文
          </button>
        )}

        <div>
          <label htmlFor="jd-text" className="block text-sm font-medium">
            岗位描述（粘贴）
          </label>
          <textarea
            id="jd-text"
            className="mt-1 h-40 w-full rounded-lg border border-neutral-300 p-3 text-base"
            placeholder="粘贴 JD 全文…"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>
        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            className="mt-1"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            required
          />
          <span>
            我已阅读并同意{" "}
            <Link href="/privacy" className="underline">
              隐私说明
            </Link>
            （含第三方模型处理；生产环境默认 24 小时内自动删除，本地可手动删除）
          </span>
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "分析中…" : "开始诊断"}
        </button>
      </form>

      <p className="mt-8 text-xs text-neutral-500">
        诊断会调用第三方云模型（DeepSeek）。本地联调数据在进程重启前保留或可在结果页删除；生产环境默认
        24 小时内自动删除。不用于模型训练。
      </p>
    </main>
  );
}
