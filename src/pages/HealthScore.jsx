import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartShell } from "../components/ChartShell";
import { ScoreBar } from "../components/ScoreBar";
import { buildHealthScores, formatCurrency } from "../lib/metrics";

export function HealthScore({ bookings }) {
  const scores = buildHealthScores(bookings);

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-panel">
        <div className="mb-5">
          <h2 className="text-base font-semibold text-zinc-950">Leaderboard Ranking</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Health Score = 40% Revenue Performance + 25% Occupancy Demand + 20% Booking Reliability + 15% Channel
            Diversity.
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-5">
          {scores.map((item) => (
            <article key={item.property} className="rounded-lg border border-zinc-200 bg-stone-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-md bg-zinc-950 px-2 py-1 text-xs font-semibold text-white">#{item.rank}</span>
                <span className="text-xl font-semibold text-zinc-950">{item.healthScore.toFixed(1)}</span>
              </div>
              <h3 className="mt-4 min-h-12 text-base font-semibold text-zinc-950">{item.property}</h3>
              <p className="mt-1 text-sm text-zinc-500">{formatCurrency(item.revenue)} realized revenue</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartShell title="Score Breakdown Chart" subtitle="Normalized component scores on a 0-100 scale">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scores} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="property" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" domain={[0, 100]} />
              <Tooltip formatter={(value) => [Number(value).toFixed(1), "Score"]} />
              <Legend />
              <Bar dataKey="revenueScore" name="Revenue" fill="#059669" radius={[4, 4, 0, 0]} />
              <Bar dataKey="demandScore" name="Demand" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              <Bar dataKey="reliabilityScore" name="Reliability" fill="#d97706" radius={[4, 4, 0, 0]} />
              <Bar dataKey="channelDiversity" name="Channel Diversity" fill="#0891b2" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>

        <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-base font-semibold text-zinc-950">Component Detail</h2>
          <div className="mt-5 space-y-6">
            {scores.map((item) => (
              <div key={item.property} className="rounded-lg border border-zinc-100 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="font-semibold text-zinc-950">{item.property}</h3>
                  <span className="text-sm font-semibold text-emerald-700">{item.healthScore.toFixed(1)} overall</span>
                </div>
                <div className="mt-4 grid gap-3">
                  <ScoreBar label="Revenue Performance" value={item.revenueScore} color="bg-emerald-500" />
                  <ScoreBar label="Occupancy Demand" value={item.demandScore} color="bg-indigo-500" />
                  <ScoreBar label="Booking Reliability" value={item.reliabilityScore} color="bg-amber-500" />
                  <ScoreBar label="Channel Diversity" value={item.channelDiversity} color="bg-cyan-500" />
                </div>
              </div>
            ))}
          </div>
        </section>
      </section>
    </div>
  );
}
