export function ChartShell({ title, subtitle, children }) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-panel">
      <div className="mb-5">
        <h2 className="text-base font-semibold text-zinc-950">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-zinc-500">{subtitle}</p> : null}
      </div>
      <div className="h-80">{children}</div>
    </section>
  );
}
