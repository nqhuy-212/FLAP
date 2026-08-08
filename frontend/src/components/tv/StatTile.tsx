import { TV_COLORS } from "./colors";

interface StatTileProps {
  value: string;
}

/**
 * Hero figure — số nguyên tự đứng, figure tỉ lệ (không tabular-nums, xem
 * marks-and-anatomy.md). Nhãn song ngữ (VI/EN) đã chuyển lên `Card`
 * title/subtitle dùng chung với các card khác — component này chỉ còn giữ
 * con số lớn.
 */
export function StatTile({ value }: StatTileProps) {
  return (
    <span className="text-[76px] font-semibold leading-none" style={{ color: TV_COLORS.textPrimary }}>
      {value}
    </span>
  );
}
