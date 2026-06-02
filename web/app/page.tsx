"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { createSession } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!consent) {
      setError("请先勾选同意隐私说明");
      return;
    }
    if (!file || !jdText.trim()) {
      setError("请上传 .docx 并粘贴岗位描述");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const { session_id } = await createSession(file, jdText.trim(), true);
      router.push(`/s/${session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">CV Doctor</h1>
      <p className="mt-2 text-neutral-600">
        上传简历（DOCX）并粘贴岗位描述，获取匹配诊断与可审阅的修改建议。本地默认联调模式；配置
        USE_REAL_PIPELINE=1 与 DEEPSEEK_API_KEY 后启用真实分析（见 server/.env.example）。
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-6">
        <div>
          <label htmlFor="resume-file" className="block text-sm font-medium">
            简历（.docx）
          </label>
          <input
            id="resume-file"
            type="file"
            accept=".docx"
            className="mt-1 block w-full text-sm"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
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
