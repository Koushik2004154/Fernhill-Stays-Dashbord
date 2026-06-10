export function parseCsv(text) {
  const rows = [];
  let field = "";
  let row = [];
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"' && inQuotes && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") {
        index += 1;
      }
      row.push(field);
      if (row.some((value) => value.length > 0)) {
        rows.push(row);
      }
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...records] = rows;
  if (!headers?.length) {
    throw new Error("CSV is empty or missing a header row.");
  }

  return records.map((record) =>
    headers.reduce((item, header, index) => {
      item[header] = record[index] ?? "";
      return item;
    }, {}),
  );
}

export function toBooking(row) {
  const nights = Number(row.nights);
  const guests = Number(row.guests);
  const nightlyRate = Number(row.nightly_rate_inr);
  const totalAmount = Number(row.total_amount_inr);
  const checkInDate = new Date(`${row.check_in_date}T00:00:00`);

  return {
    id: row.booking_id,
    property: row.property,
    checkInDate,
    checkInDateIso: row.check_in_date,
    month: row.check_in_date.slice(0, 7),
    nights,
    guests,
    roomType: row.room_type,
    channel: row.booking_channel,
    nightlyRate,
    totalAmount,
    status: row.status,
    isCancelled: row.status === "Cancelled",
    isNoShow: row.status === "No-show",
    isRealized: row.status !== "Cancelled" && row.status !== "No-show",
  };
}
