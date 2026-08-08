/** Xuất CSV phía client — không cần gọi backend, chỉ áp dụng cho dữ liệu đang lọc trên màn hình. */

function escapeCsvCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  const text = Array.isArray(value) ? value.join(";") : String(value);
  if (/[",\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

export function downloadCsv<T>(
  rows: T[],
  columns: { key: keyof T; header: string }[],
  filename: string,
): void {
  const headerLine = columns.map((c) => escapeCsvCell(c.header)).join(",");
  const lines = rows.map((row) => columns.map((c) => escapeCsvCell(row[c.key])).join(","));
  // ﻿ (BOM) để Excel nhận đúng UTF-8 — tên nhân viên/style tiếng Việt có dấu.
  const csvContent = "﻿" + [headerLine, ...lines].join("\r\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
