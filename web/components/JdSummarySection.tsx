import type { DiagnosisResult } from "@/lib/api";

export function JdSummarySection({ jd }: { jd: DiagnosisResult["jd_interpretation"] }) {
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <h2 className="text-lg font-medium">1. 岗位在招什么人</h2>
      <p className="mt-2 text-sm text-neutral-700">{jd.role_summary}</p>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-neutral-600">
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
  );
}
