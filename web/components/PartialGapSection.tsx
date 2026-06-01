import type { DiagnosisResult } from "@/lib/api";

export function PartialGapSection({
  items,
}: {
  items: DiagnosisResult["gap_report"]["partial_match"];
}) {
  if (items.length === 0) return null;
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <h2 className="text-lg font-medium">3. 部分匹配</h2>
      <ul className="mt-2 space-y-2 text-sm">
        {items.map((g, i) => (
          <li key={`pt-${i}`} className="rounded bg-amber-50 p-2 break-words">
            <strong>{g.requirement}</strong> — {g.suggestion}
          </li>
        ))}
      </ul>
    </section>
  );
}
