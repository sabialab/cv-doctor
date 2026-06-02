import type { DiagnosisResult } from "@/lib/api";

export function MatchScoreBar({ matchScore }: { matchScore: DiagnosisResult["match_score"] }) {
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <p className="text-sm font-medium text-neutral-600">匹配度</p>
      <p className="mt-1 text-xl font-medium text-neutral-800">{matchScore.overall} / 100</p>
      <p className="text-sm text-neutral-500">状态：{matchScore.status}</p>
    </section>
  );
}
