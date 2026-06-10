export function LoadingState() {
  return (
    <main className="min-h-screen bg-stone-50 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="h-20 animate-pulse rounded-lg bg-white shadow-panel" />
        <div className="grid gap-4 md:grid-cols-4">
          {[0, 1, 2, 3].map((item) => (
            <div key={item} className="h-32 animate-pulse rounded-lg bg-white shadow-panel" />
          ))}
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <div className="h-96 animate-pulse rounded-lg bg-white shadow-panel" />
          <div className="h-96 animate-pulse rounded-lg bg-white shadow-panel" />
        </div>
      </div>
    </main>
  );
}
