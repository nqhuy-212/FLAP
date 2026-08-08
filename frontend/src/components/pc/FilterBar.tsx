"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { TranslationKey } from "@/i18n/dictionaries";

export interface WipFilters {
  dateFrom: string;
  dateTo: string;
  style: string;
  color: string;
  area: string;
  workstation: string;
}

export const EMPTY_FILTERS: WipFilters = {
  dateFrom: "",
  dateTo: "",
  style: "",
  color: "",
  area: "",
  workstation: "",
};

const ALL_VALUE = "__all__";

interface FilterOptions {
  styles: string[];
  colors: string[];
  areas: string[];
  workstations: string[];
}

interface FilterBarProps {
  filters: WipFilters;
  onChange: (patch: Partial<WipFilters>) => void;
  onClear: () => void;
  options: FilterOptions;
  t: (key: TranslationKey) => string;
}

export function FilterBar({ filters, onChange, onClear, options, t }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border bg-card p-4">
      <Field label={t("dateFrom")}>
        <Input
          type="date"
          value={filters.dateFrom}
          onChange={(e) => onChange({ dateFrom: e.target.value })}
          className="w-40"
        />
      </Field>
      <Field label={t("dateTo")}>
        <Input
          type="date"
          value={filters.dateTo}
          onChange={(e) => onChange({ dateTo: e.target.value })}
          className="w-40"
        />
      </Field>
      <SelectField
        label={t("style")}
        value={filters.style}
        options={options.styles}
        onChange={(v) => onChange({ style: v })}
        allLabel={t("allOption")}
      />
      <SelectField
        label={t("color")}
        value={filters.color}
        options={options.colors}
        onChange={(v) => onChange({ color: v })}
        allLabel={t("allOption")}
      />
      <SelectField
        label={t("area")}
        value={filters.area}
        options={options.areas}
        onChange={(v) => onChange({ area: v })}
        allLabel={t("allOption")}
      />
      <SelectField
        label={t("workstation")}
        value={filters.workstation}
        options={options.workstations}
        onChange={(v) => onChange({ workstation: v })}
        allLabel={t("allOption")}
      />
      <Button variant="outline" size="sm" onClick={onClear}>
        {t("clearFilters")}
      </Button>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      {children}
    </div>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
  allLabel,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
  allLabel: string;
}) {
  return (
    <Field label={label}>
      <Select
        value={value === "" ? ALL_VALUE : value}
        onValueChange={(v) => onChange(!v || v === ALL_VALUE ? "" : v)}
      >
        <SelectTrigger className="w-40">
          {/* base-ui Select.Value mặc định hiện value thô — phải tự map sang nhãn dịch */}
          <SelectValue>{(v: string) => (v === ALL_VALUE ? allLabel : v)}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL_VALUE}>{allLabel}</SelectItem>
          {options.map((opt) => (
            <SelectItem key={opt} value={opt}>
              {opt}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </Field>
  );
}
