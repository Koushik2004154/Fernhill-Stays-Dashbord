import { useEffect, useMemo, useState } from "react";
import csvText from "../../data/cleaned_bookings.csv?raw";
import { parseCsv, toBooking } from "../lib/csv";

export function useBookings() {
  const [state, setState] = useState({ loading: true, error: null });

  const bookings = useMemo(() => {
    if (state.error || state.loading) return [];
    return parseCsv(csvText).map(toBooking);
  }, [state.error, state.loading]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const parsed = parseCsv(csvText).map(toBooking);
        const invalid = parsed.find(
          (booking) =>
            !booking.id ||
            !booking.property ||
            Number.isNaN(booking.nights) ||
            Number.isNaN(booking.totalAmount) ||
            Number.isNaN(booking.checkInDate.getTime()),
        );
        if (invalid) {
          throw new Error(`Invalid booking record found: ${invalid.id || "missing booking_id"}`);
        }
        setState({ loading: false, error: null });
      } catch (error) {
        setState({ loading: false, error });
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, []);

  return {
    bookings,
    loading: state.loading,
    error: state.error,
  };
}
