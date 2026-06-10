const navigation = [
  { id: "overview", label: "Overview" },
  { id: "property", label: "Property Performance" },
  { id: "channel", label: "Channel Analysis" },
  { id: "health", label: "Health Score" },
];

export function Layout({ activePage, onPageChange, children }) {
  return (
    <div className="min-h-screen bg-stone-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Fernhill Stays</p>
            <h1 className="mt-1 text-2xl font-semibold text-zinc-950">Booking Performance Dashboard</h1>
          </div>
          <nav className="flex gap-2 overflow-x-auto" aria-label="Dashboard pages">
            {navigation.map((item) => {
              const active = item.id === activePage;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onPageChange(item.id)}
                  className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-zinc-950 text-white"
                      : "border border-zinc-200 bg-white text-zinc-700 hover:border-zinc-400"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
