export function ScoreBar({ label, value, color = "bg-emerald-500" }) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-zinc-700">{label}</span>
        <span className="text-zinc-500">{value.toFixed(1)}</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-zinc-100">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}
