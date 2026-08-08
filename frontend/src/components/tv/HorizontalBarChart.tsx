import { TV_COLORS } from "./colors";

export interface BarDatum {
  label: string;
  value: number;
  color: string;
}

interface HorizontalBarChartProps {
  data: BarDatum[];
  /** Định dạng số hiển thị ở đầu mút cột (mặc định: dấu phẩy hàng nghìn). */
  formatValue?: (value: number) => string;
  height?: number;
  /** Kích thước hệ toạ độ SVG — khớp với bề rộng khối chứa thật để chữ không
   * bị scale nhỏ đi khi trình duyệt co viewBox lại (xem colors.ts/Card.tsx —
   * trang TV gộp 4 khối vào 1 màn hình nên mỗi khối hẹp hơn nhiều so với lúc
   * còn chiếm trọn màn hình luân phiên). */
  width?: number;
  labelColumnWidth?: number;
  valueColumnWidth?: number;
  barThickness?: number;
  labelFontSize?: number;
  valueFontSize?: number;
}

/**
 * Biểu đồ cột ngang cho danh mục có/không có thứ tự tự nhiên — 1 màu cho mỗi
 * cột theo `data[i].color` (gọi nơi dùng chọn: 1 hue phẳng cho category không
 * thứ tự, ordinal ramp cho category có thứ tự — xem anti-patterns.md).
 * Không có nhiều hơn ~4 cột nên nhãn giá trị đặt trực tiếp ở mỗi cột, không
 * cần trục lưới (mọi giá trị đã được label).
 */
export function HorizontalBarChart({
  data,
  formatValue = (v) => v.toLocaleString("en-US"),
  height,
  width = 1400,
  labelColumnWidth = 260,
  valueColumnWidth = 160,
  barThickness = 24, // ≤24px theo mark spec
  labelFontSize = 30,
  valueFontSize = 32,
}: HorizontalBarChartProps) {
  const bandHeight = height ?? 96;
  const maxValue = Math.max(1, ...data.map((d) => d.value));
  const innerWidth = width - labelColumnWidth - valueColumnWidth;
  const svgHeight = data.length * bandHeight;

  return (
    <svg
      viewBox={`0 0 ${width} ${svgHeight}`}
      width="100%"
      height={svgHeight}
      role="img"
      aria-label="Biểu đồ cột ngang"
    >
      {data.map((d, i) => {
        const barWidth = Math.max(0, (d.value / maxValue) * innerWidth);
        const y = i * bandHeight;
        const barY = y + (bandHeight - barThickness) / 2;
        return (
          <g key={d.label}>
            <text
              x={labelColumnWidth - 20}
              y={y + bandHeight / 2}
              textAnchor="end"
              dominantBaseline="middle"
              fontSize={labelFontSize}
              fill={TV_COLORS.textSecondary}
            >
              {d.label}
            </text>
            {/* Baseline — trục đơn mà mọi cột mọc ra từ đó */}
            <line
              x1={labelColumnWidth}
              y1={y + 4}
              x2={labelColumnWidth}
              y2={y + bandHeight - 4}
              stroke={TV_COLORS.baseline}
              strokeWidth={1}
            />
            <rect
              x={labelColumnWidth}
              y={barY}
              width={barWidth}
              height={barThickness}
              rx={4}
              fill={d.color}
            />
            <text
              x={labelColumnWidth + barWidth + 20}
              y={y + bandHeight / 2}
              textAnchor="start"
              dominantBaseline="middle"
              fontSize={valueFontSize}
              fontWeight={600}
              fill={TV_COLORS.textPrimary}
            >
              {formatValue(d.value)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
