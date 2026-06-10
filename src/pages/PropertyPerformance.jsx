import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartShell } from "../components/ChartShell";
import { MetricTable } from "../components/MetricTable";
import { buildPropertyPerformance, formatCurrency, formatNumber, formatPercent } from "../lib/metrics";

export function PropertyPerformance({ bookings }) {
  const rows = buildPropertyPerformance(bookings);

  return (
    <div className="space-y-6">
      <section className="grid gap-5 xl:grid-cols-2">
        <ChartShell title="Revenue by Property" subtitle="Realized revenue excludes Cancelled and No-show bookings">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} layout="vertical" margin={{ top: 10, right: 20, left: 88, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis type="number" stroke="#71717a" tickFormatter={(value) => `₹${Math.round(value / 1000)}k`} />
              <YAxis type="category" dataKey="property" stroke="#71717a" width={120} />
              <Tooltip formatter={(value) => [formatCurrency(value), "Revenue"]} />
              <Bar dataKey="revenue" fill="#0f766e" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Booking Count by Property" subtitle="Cleaned booking records by property">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="property" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" allowDecimals={false} />
              <Tooltip formatter={(value) => [formatNumber(value), "Bookings"]} />
              <Bar dataKey="bookings" fill="#d97706" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <MetricTable rows={rows} type="property" />
        <ChartShell title="Cancellation Rate by Property" subtitle="Cancelled bookings as a share of all bookings">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="property" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" tickFormatter={(value) => `${value}%`} />
              <Tooltip formatter={(value) => [formatPercent(value), "Cancellation Rate"]} />
              <Legend />
              <Bar dataKey="cancellationRate" name="Cancellation Rate" fill="#e11d48" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>
    </div>
  );
}
