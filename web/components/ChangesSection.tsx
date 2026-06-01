"use client";

import { FREE_CHANGE_LIMIT } from "@/lib/constants";
import type { DiagnosisResult } from "@/lib/api";

import { DiffCard, type DiffCardProps } from "./DiffCard";

type ChangesSectionProps = {
  changes: DiagnosisResult["changes"];
  freeLimit?: number;
  confirmAcceptId: string | null;
  exportLink: string | null;
  onExport: () => void;
  onAccept: DiffCardProps["onAccept"];
  onReject: DiffCardProps["onReject"];
  onSaveEdit: DiffCardProps["onSaveEdit"];
  onCancelConfirm: () => void;
};

export function ChangesSection({
  changes,
  freeLimit = FREE_CHANGE_LIMIT,
  confirmAcceptId,
  exportLink,
  onExport,
  onAccept,
  onReject,
  onSaveEdit,
  onCancelConfirm,
}: ChangesSectionProps) {
  const total = Math.min(changes.length, freeLimit);
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <h2 className="text-lg font-medium">5. 简历手术建议（免费 {freeLimit} 条）</h2>
      <div className="mt-4 space-y-4">
        {changes.map((ch, i) => (
          <DiffCard
            key={ch.id}
            index={i + 1}
            total={total}
            change={ch}
            confirmAcceptId={confirmAcceptId}
            onAccept={onAccept}
            onReject={onReject}
            onSaveEdit={onSaveEdit}
            onCancelConfirm={onCancelConfirm}
          />
        ))}
      </div>
      <button
        type="button"
        onClick={onExport}
        className="mt-4 min-h-[44px] rounded-lg border border-neutral-900 px-4 py-2 text-sm"
      >
        导出已采纳修改为 Word（.docx）
      </button>
      {exportLink && (
        <a
          href={exportLink}
          download="resume-export.docx"
          className="mt-2 block min-h-[44px] text-sm leading-[44px] text-blue-700 underline"
        >
          下载 Word 文档
        </a>
      )}
    </section>
  );
}
