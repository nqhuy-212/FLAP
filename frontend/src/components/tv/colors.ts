/**
 * Bảng màu TV — luôn tối, không theo theme hệ điều hành (TV treo tường, xem
 * skill dataviz). `pagePlane` = `#002B36` theo yêu cầu người dùng (2026-08-08)
 * — đây chính là "base03" của bảng màu Solarized Dark. `surface` (nền card)
 * dùng `#073642` — "base02" của cùng bảng Solarized, bậc sáng hơn liền kề
 * `base03` nên phối hài hoà cùng tông thay vì ghép một xám trung tính lệch
 * tông như bản trước đó (`#1e1e1e`/`#252526`, theo nền editor VS Code — đã
 * thay bằng yêu cầu Solarized này).
 *
 * Toàn bộ hue dữ liệu (singleSeries, AGE_BUCKET_RAMP) đã chạy lại
 * `validate_palette.js --surface "#073642" --mode dark` cho đúng nền card
 * mới — PASS. Bậc tối nhất của AGE_BUCKET_RAMP phải đổi từ `#1c5cab` (step
 * 550, PASS trên `#252526` nhưng chỉ 1.96:1 trên `#073642` tối hơn → FAIL)
 * sang ramp giãn cách rộng hơn `#9ec5f4→#256abf` (step 200/300/400/500).
 */
export const TV_COLORS = {
  pagePlane: "#002B36",
  surface: "#073642",
  textPrimary: "#f2f2f0",
  textSecondary: "#9d9d9d",
  muted: "#7a7a7a",
  gridline: "#0a4553",
  baseline: "#0e5266",
  border: "rgba(255,255,255,0.08)",
  // Một hue duy nhất cho biểu đồ 1-series (area_breakdown, loading_trend) —
  // category không có thứ tự tự nhiên nên KHÔNG dùng ramp giá trị (xem
  // anti-patterns.md: "A value-ramp on nominal categories").
  singleSeries: "#3987e5",
} as const;

/** Ordinal ramp cho age_buckets (0-3/4-7/8-14/>14) — có thứ tự tự nhiên, sáng→tối. */
export const AGE_BUCKET_RAMP = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf"] as const;

/**
 * Century Gothic không phải web font miễn phí (bản quyền Monotype, không có
 * trên Google Fonts) — không thể nhúng/tải qua next/font. Khai trực tiếp
 * font-family, trình duyệt dùng bản cài sẵn trên máy (thường có sẵn qua MS
 * Office) và tự rơi về Verdana rồi sans-serif hệ thống nếu máy không có.
 */
export const TV_FONT_FAMILY = '"Century Gothic", CenturyGothic, Verdana, sans-serif';
