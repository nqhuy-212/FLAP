import { TV_COLORS } from "./colors";
import type { TopAgingItem } from "@/lib/types";
import type { TranslationKey } from "@/i18n/dictionaries";

interface TopAgingTableProps {
  items: TopAgingItem[];
  t: (key: TranslationKey) => string;
  /** Nhãn cột song ngữ — luôn cả VI và EN, độc lập với `t` (theo `?lang=` URL). */
  tVi: (key: TranslationKey) => string;
  tEn: (key: TranslationKey) => string;
}

/** Top 10 tồn lâu nhất — bảng, không phải biểu đồ (>~7 lớp mang ý nghĩa thì dùng bảng). */
export function TopAgingTable({ items, t, tVi, tEn }: TopAgingTableProps) {
  return (
    <table className="w-full border-collapse" style={{ color: TV_COLORS.textPrimary }}>
      <thead>
        <tr style={{ borderBottom: `1px solid ${TV_COLORS.baseline}` }}>
          <Th align="left" vi={tVi("columnStyle")} en={tEn("columnStyle")} />
          <Th align="left" vi={tVi("columnMo")} en={tEn("columnMo")} />
          <Th align="right" vi={tVi("columnMaxAge")} en={tEn("columnMaxAge")} />
          <Th align="right" vi={tVi("columnTrolleyCount")} en={tEn("columnTrolleyCount")} />
          <Th align="right" vi={tVi("columnQty")} en={tEn("columnQty")} />
        </tr>
      </thead>
      <tbody>
        {items.map((item, i) => (
          <tr key={`${item.mo_no}-${i}`} style={{ borderBottom: `1px solid ${TV_COLORS.gridline}` }}>
            <Td>{item.cust_style}</Td>
            <Td muted>{item.mo_no}</Td>
            <Td align="right" strong>
              {item.max_age_days} {t("days")}
            </Td>
            <Td align="right">{item.trolley_count.toLocaleString("en-US")}</Td>
            <Td align="right">{item.total_qty.toLocaleString("en-US")}</Td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Th({ vi, en, align = "left" }: { vi: string; en: string; align?: "left" | "right" }) {
  return (
    <th className="py-1.5 px-3 align-bottom" style={{ textAlign: align }}>
      <div className="text-[19px] font-medium whitespace-nowrap" style={{ color: TV_COLORS.muted }}>
        {vi}
      </div>
      <div className="text-[17px] whitespace-nowrap" style={{ color: TV_COLORS.muted, opacity: 0.78 }}>
        {en}
      </div>
    </th>
  );
}

function Td({
  children,
  align = "left",
  muted,
  strong,
}: {
  children: React.ReactNode;
  align?: "left" | "right";
  muted?: boolean;
  strong?: boolean;
}) {
  return (
    <td
      className="py-1.5 px-3 text-[21px] whitespace-nowrap"
      style={{
        textAlign: align,
        color: muted ? TV_COLORS.textSecondary : TV_COLORS.textPrimary,
        fontWeight: strong ? 600 : 400,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      {children}
    </td>
  );
}
