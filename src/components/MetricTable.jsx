import { formatCurrency, formatNumber, formatPercent } from "../lib/metrics";

export function MetricTable({ rows, type }) {
  const isProperty = type === "property";

  return (
    <section className="overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-panel">
      <div className="border-b border-zinc-200 p-5">
        <h2 className="text-base font-semibold text-zinc-950">
          {isProperty ? "Property Ranking Table" : "Channel Contribution Table"}
        </h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-zinc-200 text-sm">
          <thead className="bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-500">
            <tr>
              <th className="px-5 py-3">{isProperty ? "Property" : "Channel"}</th>
              <th className="px-5 py-3 text-right">Revenue</th>
              <th className="px-5 py-3 text-right">Bookings</th>
              <th className="px-5 py-3 text-right">Cancellation Rate</th>
              {!isProperty ? <th className="px-5 py-3 text-right">Contribution</th> : null}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {rows.map((row) => (
              <tr key={row.property || row.channel} className="hover:bg-stone-50">
                <td className="px-5 py-3 font-medium text-zinc-950">{row.property || row.channel}</td>
                <td className="px-5 py-3 text-right text-zinc-700">{formatCurrency(row.revenue)}</td>
                <td className="px-5 py-3 text-right text-zinc-700">{formatNumber(row.bookings)}</td>
                <td className="px-5 py-3 text-right text-zinc-700">{formatPercent(row.cancellationRate)}</td>
                {!isProperty ? (
                  <td className="px-5 py-3 text-right text-zinc-700">{formatPercent(row.contribution)}</td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
