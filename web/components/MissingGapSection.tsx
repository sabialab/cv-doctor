import type { DiagnosisResult } from "@/lib/api";

export function MissingGapSection({
  hardMissing,
  preferredMissing,
}: {
  hardMissing: DiagnosisResult["gap_report"]["hard_missing"];
  preferredMissing: DiagnosisResult["gap_report"]["preferred_missing"];
}) {
  if (hardMissing.length === 0 && preferredMissing.length === 0) return null;
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <h2 className="text-lg font-medium">4. 缺失项</h2>
      <p className="mt-2 text-sm text-neutral-600">
        以下缺口不会自动写入简历，仅作待补充建议（请勿编造经历）。
      </p>
      <ul className="mt-3 space-y-2 text-sm">
        {hardMissing.map((g, i) => (
          <li key={`hm-${i}`} className="rounded bg-red-50 p-2 break-words">
            <strong>{g.requirement}</strong> — {g.suggestion}
          </li>
        ))}
        {preferredMissing.map((g, i) => (
          <li key={`pm-${i}`} className="rounded bg-amber-50 p-2 break-words">
            {g.requirement} — {g.suggestion}
          </li>
        ))}
      </ul>
    </section>
  );
}
