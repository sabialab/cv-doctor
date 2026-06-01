export function MatchedSection({ matched }: { matched: string[] }) {
  if (matched.length === 0) return null;
  return (
    <section className="rounded-xl border border-neutral-200 p-5">
      <h2 className="text-lg font-medium">2. 你已匹配</h2>
      <ul className="mt-2 space-y-1 text-sm">
        {matched.map((m, i) => (
          <li key={`m-${i}`} className="rounded bg-green-50 p-2 break-words">
            {m}
          </li>
        ))}
      </ul>
    </section>
  );
}
