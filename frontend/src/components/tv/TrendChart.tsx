import { TV_COLORS } from "./colors";

export interface TrendPoint {
  date: string;
  value: number;
}

interface TrendChartProps {
  data: TrendPoint[];
  formatValue?: (value: number) => string;
  /** Kích thước hệ toạ độ SVG — khớp bề rộng khối chứa thật, xem ghi chú
   * tương tự trong HorizontalBarChart.tsx. */
  width?: number;
  height?: number;
}

const Y_TICKS = 3;

/**
 * Biểu đồ đường + vùng cho 1 chuỗi theo thời gian (loading_trend). 1 hue duy
 * nhất — trục X theo thứ tự ngày (khoảng cách đều theo chỉ số, không theo mốc
 * thời gian thật vì dữ liệu đã gộp theo ngày). Nhãn trực tiếp chỉ đặt ở điểm
 * cuối; các giá trị còn lại đọc qua trục lưới.
 */
export function TrendChart({
  data,
  formatValue = (v) => v.toLocaleString("en-US"),
  width = 1700,
  height = 560,
}: TrendChartProps) {
  if (data.length === 0) return null;

  const padding = { top: 32, right: 24, bottom: 44, left: 64 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(1, ...data.map((d) => d.value)) * 1.15;

  const xFor = (i: number) => padding.left + (data.length === 1 ? 0 : (i / (data.length - 1)) * innerWidth);
  const yFor = (v: number) => padding.top + innerHeight - (v / maxValue) * innerHeight;

  const linePath = data.map((d, i) => `${i === 0 ? "M" : "L"} ${xFor(i)} ${yFor(d.value)}`).join(" ");
  const areaPath = `${linePath} L ${xFor(data.length - 1)} ${padding.top + innerHeight} L ${xFor(0)} ${padding.top + innerHeight} Z`;

  const yTicks = Array.from({ length: Y_TICKS + 1 }, (_, i) => (maxValue / Y_TICKS) * i);
  const xTickIndices = data.length <= 1 ? [0] : [0, Math.floor((data.length - 1) / 2), data.length - 1];
  const last = data[data.length - 1];

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label="Biểu đồ xu hướng">
      {yTicks.map((tick) => (
        <g key={tick}>
          <line
            x1={padding.left}
            y1={yFor(tick)}
            x2={width - padding.right}
            y2={yFor(tick)}
            stroke={TV_COLORS.gridline}
            strokeWidth={1}
          />
          <text x={padding.left - 14} y={yFor(tick)} textAnchor="end" dominantBaseline="middle" fontSize={20} fill={TV_COLORS.muted}>
            {Math.round(tick).toLocaleString("en-US")}
          </text>
        </g>
      ))}

      <path d={areaPath} fill={TV_COLORS.singleSeries} opacity={0.12} stroke="none" />
      <path d={linePath} fill="none" stroke={TV_COLORS.singleSeries} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round" />

      {xTickIndices.map((i) => (
        <text
          key={i}
          x={xFor(i)}
          y={height - padding.bottom + 30}
          textAnchor="middle"
          fontSize={20}
          fill={TV_COLORS.muted}
        >
          {formatTickDate(data[i].date)}
        </text>
      ))}

      {/* Điểm cuối — marker ≥8px + viền surface + nhãn giá trị trực tiếp */}
      <circle cx={xFor(data.length - 1)} cy={yFor(last.value)} r={7} fill={TV_COLORS.singleSeries} stroke={TV_COLORS.surface} strokeWidth={2} />
      <text
        x={xFor(data.length - 1)}
        y={yFor(last.value) - 18}
        textAnchor="end"
        fontSize={26}
        fontWeight={600}
        fill={TV_COLORS.textPrimary}
      >
        {formatValue(last.value)}
      </text>
    </svg>
  );
}

function formatTickDate(iso: string): string {
  const [, month, day] = iso.split("-");
  return `${day}/${month}`;
}
