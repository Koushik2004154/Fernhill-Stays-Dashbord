import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartShell } from "../components/ChartShell";
import { MetricTable } from "../components/MetricTable";
import { buildChannelAnalysis, formatCurrency, formatNumber, formatPercent } from "../lib/metrics";

const COLORS = ["#059669", "#4f46e5", "#d97706", "#0891b2", "#e11d48", "#7c3aed"];

export function ChannelAnalysis({ bookings }) {
  const rows = buildChannelAnalysis(bookings);

  return (
    <div className="space-y-6">
      <section className="grid gap-5 xl:grid-cols-2">
        <ChartShell title="Revenue by Channel" subtitle="Realized revenue by acquisition source">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="channel" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" tickFormatter={(value) => `₹${Math.round(value / 1000)}k`} />
              <Tooltip formatter={(value) => [formatCurrency(value), "Revenue"]} />
              <Bar dataKey="revenue" radius={[6, 6, 0, 0]}>
                {rows.map((row, index) => (
                  <Cell key={row.channel} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Channel Contribution %" subtitle="Share of realized revenue by channel">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={rows} dataKey="contribution" nameKey="channel" innerRadius={72} outerRadius={120} paddingAngle={2}>
                {rows.map((row, index) => (
                  <Cell key={row.channel} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [formatPercent(value), "Contribution"]} />
            </PieChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartShell title="Booking Count by Channel" subtitle="Cleaned booking records by channel">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="channel" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" allowDecimals={false} />
              <Tooltip formatter={(value) => [formatNumber(value), "Bookings"]} />
              <Bar dataKey="bookings" fill="#0891b2" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Cancellation Rate by Channel" subtitle="Cancelled bookings as a share of channel bookings">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="channel" stroke="#71717a" interval={0} angle={-18} textAnchor="end" height={72} />
              <YAxis stroke="#71717a" tickFormatter={(value) => `${value}%`} />
              <Tooltip formatter={(value) => [formatPercent(value), "Cancellation Rate"]} />
              <Bar dataKey="cancellationRate" fill="#e11d48" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <MetricTable rows={rows} type="channel" />
    </div>
  );
}
