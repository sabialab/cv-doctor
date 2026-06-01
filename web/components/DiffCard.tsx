"use client";

import { useState } from "react";

import type { DiagnosisResult } from "@/lib/api";

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

function TextBlock({ label, text }: { label: string; text: string }) {
  if (text.length <= 120) {
    return (
      <p className={label === "原文" ? "mt-2 line-through text-neutral-500" : "mt-1 font-medium text-green-800"}>
        <span className="text-xs text-neutral-400">{label}：</span> {text}
      </p>
    );
  }
  return (
    <details className="mt-2 text-sm">
      <summary className="cursor-pointer text-neutral-600">{label}</summary>
      <p className={label === "原文" ? "mt-1 line-through text-neutral-500" : "mt-1 font-medium text-green-800"}>
        {text}
      </p>
    </details>
  );
}

export function DiffCard({
  index,
  total,
  change: ch,
  confirmAcceptId,
  onAccept,
  onReject,
  onSaveEdit,
  onCancelConfirm,
}: DiffCardProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(ch.revised);
  const [saving, setSaving] = useState(false);

  const needsGate = ch.risk_level === "high" || ch.requires_user_confirmation;

  async function handleSave() {
    if (!draft.trim()) return;
    setSaving(true);
    try {
      await onSaveEdit(ch.id, draft.trim());
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-lg bg-neutral-50 p-4 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-medium text-neutral-800">
          建议 {index}/{total}
        </p>
        <span className="text-xs text-neutral-500">{ch.section}</span>
        {(ch.risk_level === "medium" || ch.risk_level === "high") && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-900">
            风险：{ch.risk_level}
            {ch.requires_user_confirmation ? "（建议确认）" : ""}
          </span>
        )}
      </div>
      {editing ? (
        <div className="mt-3 space-y-2">
          <textarea
            className="w-full rounded border border-neutral-300 p-2 text-base"
            rows={4}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={saving}
              onClick={handleSave}
              className="min-h-[44px] rounded bg-green-700 px-3 py-2 text-xs text-white disabled:opacity-50"
            >
              {saving ? "保存中…" : "保存并采纳"}
            </button>
            <button
              type="button"
              onClick={() => {
                setEditing(false);
                setDraft(ch.revised);
              }}
              className="min-h-[44px] rounded border border-neutral-300 px-3 py-2 text-xs"
            >
              取消
            </button>
          </div>
        </div>
      ) : (
        <>
          <TextBlock label="原文" text={ch.original} />
          <TextBlock label="建议" text={ch.revised} />
          <p className="mt-2 text-neutral-600">{ch.reason}</p>
          <div className="mt-2 rounded bg-white/80 p-2 text-xs text-neutral-600">
            <p className="font-medium text-neutral-700">依据</p>
            {ch.source_label ? <p className="mt-1">{ch.source_label}</p> : null}
            {ch.evidence_ids.length > 0 ? (
              <p className="mt-1 text-neutral-500">证据：{ch.evidence_ids.join("、")}</p>
            ) : null}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {confirmAcceptId === ch.id ? (
              <>
                <p className="w-full text-xs text-amber-900">
                  {needsGate
                    ? "此为高风险修改，请确认内容属实后再采纳。"
                    : "请确认后再采纳。"}
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
                  onClick={onCancelConfirm}
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
                <button
                  type="button"
                  onClick={() => {
                    setDraft(ch.revised);
                    setEditing(true);
                  }}
                  className="min-h-[44px] rounded border border-neutral-300 px-3 py-2 text-xs"
                >
                  编辑
                </button>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
