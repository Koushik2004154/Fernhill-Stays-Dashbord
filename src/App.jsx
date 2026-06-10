import { useState } from "react";
import { EmptyState } from "./components/EmptyState";
import { ErrorState } from "./components/ErrorState";
import { Layout } from "./components/Layout";
import { LoadingState } from "./components/LoadingState";
import { useBookings } from "./hooks/useBookings";
import { ChannelAnalysis } from "./pages/ChannelAnalysis";
import { HealthScore } from "./pages/HealthScore";
import { Overview } from "./pages/Overview";
import { PropertyPerformance } from "./pages/PropertyPerformance";

const pages = {
  overview: Overview,
  property: PropertyPerformance,
  channel: ChannelAnalysis,
  health: HealthScore,
};

export default function App() {
  const [activePage, setActivePage] = useState("overview");
  const { bookings, loading, error } = useBookings();

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!bookings.length) return <EmptyState />;

  const Page = pages[activePage] || Overview;

  return (
    <Layout activePage={activePage} onPageChange={setActivePage}>
      <Page bookings={bookings} />
    </Layout>
  );
}
