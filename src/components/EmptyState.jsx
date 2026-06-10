export function EmptyState() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-stone-50 p-6">
      <section className="max-w-md rounded-lg border border-zinc-200 bg-white p-6 text-center shadow-panel">
        <p className="text-sm font-semibold uppercase tracking-wide text-amber-700">No data</p>
        <h1 className="mt-2 text-xl font-semibold text-zinc-950">No cleaned bookings are available</h1>
        <p className="mt-2 text-sm text-zinc-600">
          Generate `data/cleaned_bookings.csv` and restart the Vite dev server.
        </p>
      </section>
    </main>
  );
}
