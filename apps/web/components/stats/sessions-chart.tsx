"use client";

import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  type TooltipContentProps,
} from "recharts";
import { CircleCheck, CircleX, Table2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { SessionHistoryItem } from "@/lib/api/stats.api";

function formatDateLabel(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function ChartTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0]?.payload as SessionHistoryItem;

  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-sm shadow-sm">
      <p className="mb-1 font-medium text-popover-foreground">{formatDateLabel(item.date)}</p>
      <p className="text-status-good">
        <span className="font-semibold">{item.correct}</span> correct
      </p>
      <p className="text-status-critical">
        <span className="font-semibold">{item.incorrect}</span> incorrect
      </p>
      <p className="text-xs text-muted-foreground">{Math.round(item.accuracy)}% accuracy</p>
    </div>
  );
}

/**
 * Correct/incorrect is a status pair (good/critical), not a categorical
 * series pick — validated against Soulee's surfaces with the dataviz skill's
 * script. Red/green fails deuteranopia separation (ΔE 4.1) regardless of the
 * exact hue, so color never carries the distinction alone: every use pairs
 * it with an icon + label (legend, tooltip) and a plain-table fallback exists.
 */
export function SessionsChart({ data }: { data: SessionHistoryItem[] }) {
  const [showTable, setShowTable] = useState(false);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <CircleCheck className="size-3.5 text-status-good" />
            Correct
          </span>
          <span className="inline-flex items-center gap-1">
            <CircleX className="size-3.5 text-status-critical" />
            Incorrect
          </span>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setShowTable((v) => !v)}>
          <Table2 className="size-3.5" />
          {showTable ? "View chart" : "View table"}
        </Button>
      </div>

      {showTable ? (
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted-foreground">
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Sessions</th>
                <th className="px-3 py-2">Correct</th>
                <th className="px-3 py-2">Incorrect</th>
                <th className="px-3 py-2">Accuracy</th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {data.map((item) => (
                <tr key={item.date} className="border-b border-border last:border-0">
                  <td className="px-3 py-2">{formatDateLabel(item.date)}</td>
                  <td className="px-3 py-2">{item.sessions}</td>
                  <td className="px-3 py-2">{item.correct}</td>
                  <td className="px-3 py-2">{item.incorrect}</td>
                  <td className="px-3 py-2">{Math.round(item.accuracy)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} barCategoryGap="20%">
              <CartesianGrid vertical={false} stroke="var(--border)" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDateLabel}
                tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                axisLine={{ stroke: "var(--border)" }}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={28}
              />
              <Tooltip content={ChartTooltip} cursor={{ fill: "var(--accent)" }} />
              <Bar
                dataKey="correct"
                stackId="a"
                fill="var(--status-good)"
                stroke="var(--background)"
                strokeWidth={2}
                maxBarSize={20}
              />
              <Bar
                dataKey="incorrect"
                stackId="a"
                fill="var(--status-critical)"
                stroke="var(--background)"
                strokeWidth={2}
                maxBarSize={20}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
