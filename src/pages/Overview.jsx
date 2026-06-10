import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartShell } from "../components/ChartShell";
import { KpiCard } from "../components/KpiCard";
import { buildOverview, formatCurrency, formatNumber, formatPercent } from "../lib/metrics";

export function Overview({ bookings }) {
  const overview = buildOverview(bookings);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total Revenue" value={formatCurrency(overview.totalRevenue)} helper="Realized revenue only" />
        <KpiCard
          label="Total Bookings"
          value={formatNumber(overview.totalBookings)}
          helper="All cleaned bookings"
          accent="indigo"
        />
        <KpiCard
          label="Average Booking Value"
          value={formatCurrency(overview.averageBookingValue)}
          helper="Realized revenue over all bookings"
          accent="amber"
        />
        <KpiCard
          label="Cancellation Rate"
          value={formatPercent(overview.cancellationRate)}
          helper="Cancelled bookings over total"
          accent="rose"
        />
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <ChartShell title="Revenue Trend" subtitle="Monthly realized revenue, excluding Cancelled and No-show bookings">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={overview.revenueTrend} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <defs>
                <linearGradient id="revenueFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="month" stroke="#71717a" />
              <YAxis stroke="#71717a" tickFormatter={(value) => `₹${Math.round(value / 1000)}k`} />
              <Tooltip formatter={(value) => [formatCurrency(value), "Revenue"]} />
              <Area type="monotone" dataKey="revenue" stroke="#059669" strokeWidth={3} fill="url(#revenueFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Booking Trend" subtitle="Monthly booking volume across all cleaned records">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={overview.bookingTrend} margin={{ top: 10, right: 18, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#e4e4e7" strokeDasharray="3 3" />
              <XAxis dataKey="month" stroke="#71717a" />
              <YAxis stroke="#71717a" allowDecimals={false} />
              <Tooltip formatter={(value) => [formatNumber(value), "Bookings"]} />
              <Bar dataKey="bookings" fill="#4f46e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>
    </div>
  );
}
