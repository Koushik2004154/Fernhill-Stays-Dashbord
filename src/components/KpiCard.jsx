export function KpiCard({ label, value, helper, accent = "emerald" }) {
  const colors = {
    emerald: "border-l-emerald-500",
    indigo: "border-l-indigo-500",
    amber: "border-l-amber-500",
    rose: "border-l-rose-500",
    cyan: "border-l-cyan-500",
  };

  return (
    <article className={`rounded-lg border border-zinc-200 border-l-4 bg-white p-5 shadow-panel ${colors[accent]}`}>
      <p className="text-sm font-medium text-zinc-500">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-zinc-950">{value}</p>
      {helper ? <p className="mt-2 text-sm text-zinc-500">{helper}</p> : null}
    </article>
  );
}
