import type { DiagnosisResult } from "@/lib/api";

export function PolicyGuardBanner({
  policyGuard,
}: {
  policyGuard: NonNullable<DiagnosisResult["policy_guard"]>;
}) {
  if (policyGuard.passed || policyGuard.warnings.length === 0) return null;
  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50 p-5">
      <h2 className="text-lg font-medium">合规提示</h2>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-900">
        {policyGuard.warnings.map((w, i) => (
          <li key={`pg-${i}`}>{w}</li>
        ))}
      </ul>
    </section>
  );
}
