export function ErrorState({ error }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-stone-50 p-6">
      <section className="max-w-xl rounded-lg border border-rose-200 bg-white p-6 shadow-panel">
        <p className="text-sm font-semibold uppercase tracking-wide text-rose-700">Data error</p>
        <h1 className="mt-2 text-xl font-semibold text-zinc-950">The dashboard could not load bookings</h1>
        <p className="mt-2 rounded-md bg-rose-50 p-3 text-sm text-rose-900">{error?.message || "Unknown error"}</p>
      </section>
    </main>
  );
}
