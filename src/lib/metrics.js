const INR_FORMATTER = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const NUMBER_FORMATTER = new Intl.NumberFormat("en-IN");

export function formatCurrency(value) {
  return INR_FORMATTER.format(value || 0);
}

export function formatNumber(value) {
  return NUMBER_FORMATTER.format(value || 0);
}

export function formatPercent(value) {
  return `${(value || 0).toFixed(1)}%`;
}

export function realizedRevenue(bookings) {
  return bookings.filter((booking) => booking.isRealized).reduce((sum, booking) => sum + booking.totalAmount, 0);
}

export function cancellationRate(bookings) {
  if (!bookings.length) return 0;
  return (bookings.filter((booking) => booking.isCancelled).length / bookings.length) * 100;
}

export function reliabilityRate(bookings) {
  if (!bookings.length) return 0;
  const failed = bookings.filter((booking) => booking.isCancelled || booking.isNoShow).length;
  return ((bookings.length - failed) / bookings.length) * 100;
}

export function groupBy(items, keyGetter) {
  return items.reduce((groups, item) => {
    const key = keyGetter(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
    return groups;
  }, new Map());
}

export function sum(items, getter) {
  return items.reduce((total, item) => total + getter(item), 0);
}

export function normalize(value, max) {
  if (!max || max <= 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

export function buildOverview(bookings) {
  const revenue = realizedRevenue(bookings);
  const totalBookings = bookings.length;
  const averageBookingValue = totalBookings ? revenue / totalBookings : 0;

  const byMonth = Array.from(groupBy(bookings, (booking) => booking.month).entries())
    .map(([month, rows]) => ({
      month,
      revenue: realizedRevenue(rows),
      bookings: rows.length,
    }))
    .sort((a, b) => a.month.localeCompare(b.month));

  return {
    totalRevenue: revenue,
    totalBookings,
    averageBookingValue,
    cancellationRate: cancellationRate(bookings),
    revenueTrend: byMonth,
    bookingTrend: byMonth,
  };
}

export function buildPropertyPerformance(bookings) {
  return Array.from(groupBy(bookings, (booking) => booking.property).entries())
    .map(([property, rows]) => {
      const revenue = realizedRevenue(rows);
      return {
        property,
        revenue,
        bookings: rows.length,
        realizedBookings: rows.filter((booking) => booking.isRealized).length,
        nights: sum(rows.filter((booking) => booking.isRealized), (booking) => booking.nights),
        cancellationRate: cancellationRate(rows),
        averageBookingValue: rows.length ? revenue / rows.length : 0,
      };
    })
    .sort((a, b) => b.revenue - a.revenue);
}

export function buildChannelAnalysis(bookings) {
  const totalRevenue = realizedRevenue(bookings);
  return Array.from(groupBy(bookings, (booking) => booking.channel).entries())
    .map(([channel, rows]) => {
      const revenue = realizedRevenue(rows);
      return {
        channel,
        revenue,
        bookings: rows.length,
        cancellationRate: cancellationRate(rows),
        contribution: totalRevenue ? (revenue / totalRevenue) * 100 : 0,
      };
    })
    .sort((a, b) => b.revenue - a.revenue);
}

function channelDiversityScore(rows, maxChannels) {
  const realized = rows.filter((booking) => booking.isRealized);
  if (!realized.length || maxChannels <= 1) return 0;
  const channelCounts = Array.from(groupBy(realized, (booking) => booking.channel).values()).map((items) => items.length);
  const entropy = channelCounts.reduce((total, count) => {
    const share = count / realized.length;
    return total - share * Math.log(share);
  }, 0);
  return normalize(entropy, Math.log(maxChannels));
}

export function buildHealthScores(bookings) {
  const properties = buildPropertyPerformance(bookings);
  const maxRevenue = Math.max(...properties.map((item) => item.revenue), 0);
  const maxNights = Math.max(...properties.map((item) => item.nights), 0);
  const maxChannels = new Set(bookings.map((booking) => booking.channel)).size;

  return properties
    .map((property) => {
      const rows = bookings.filter((booking) => booking.property === property.property);
      const revenueScore = normalize(property.revenue, maxRevenue);
      const demandScore = normalize(property.nights, maxNights);
      const reliabilityScore = reliabilityRate(rows);
      const channelDiversity = channelDiversityScore(rows, maxChannels);
      const healthScore =
        revenueScore * 0.4 + demandScore * 0.25 + reliabilityScore * 0.2 + channelDiversity * 0.15;

      return {
        property: property.property,
        healthScore,
        revenueScore,
        demandScore,
        reliabilityScore,
        channelDiversity,
        revenue: property.revenue,
        bookings: property.bookings,
      };
    })
    .sort((a, b) => b.healthScore - a.healthScore)
    .map((item, index) => ({ ...item, rank: index + 1 }));
}
