import { TV_COLORS } from "./colors";

interface CardProps {
  /** Tiêu đề tiếng Việt — dòng chính. */
  title?: string;
  /** Tiêu đề tiếng Anh — dòng phụ nhỏ hơn ngay dưới, cùng kiểu với tiêu đề trang (song ngữ). */
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * Card chrome dùng chung cho mọi khối trên trang TV gộp 1 màn hình — nền
 * `TV_COLORS.surface`, viền hairline + bo góc để phân lớp rõ với `pagePlane`,
 * tiêu đề (nếu có) ở ink phụ theo đúng quy tắc "text luôn dùng text token,
 * không dùng màu series" (marks-and-anatomy.md).
 */
export function Card({ title, subtitle, children, className }: CardProps) {
  return (
    <div
      className={`flex flex-col overflow-hidden rounded-2xl ${className ?? ""}`}
      style={{
        backgroundColor: TV_COLORS.surface,
        border: `1px solid ${TV_COLORS.border}`,
        boxShadow: "0 1px 2px rgba(0,0,0,0.35)",
      }}
    >
      {title && (
        <div className="px-8 pt-6">
          <h2
            className="text-[22px] font-medium tracking-wide uppercase whitespace-nowrap"
            style={{ color: TV_COLORS.muted, letterSpacing: "0.03em" }}
          >
            {title}
          </h2>
          {subtitle && (
            <p className="text-[20px] whitespace-nowrap" style={{ color: TV_COLORS.muted, opacity: 0.78 }}>
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div className="flex flex-1 flex-col justify-center px-8 pb-6 pt-2">{children}</div>
    </div>
  );
}
