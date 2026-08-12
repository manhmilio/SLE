import type { components } from "@repo/types";

type ProgressSummary = components["schemas"]["ProgressSummary"];

/** not_started -> learning -> known is a progression, so it's ordinal: one hue,
 *  monotone lightness — lighter sage for "earlier" stages, primary for "known". */
const STAGES = [
  { key: "not_started" as const, label: "Not started", colorVar: "var(--sage-200)" },
  { key: "learning" as const, label: "Learning", colorVar: "var(--sage-400)" },
  { key: "known" as const, label: "Known", colorVar: "var(--sage-600)" },
];

export function SetProgressSummary({ summary }: { summary: ProgressSummary }) {
  const total = summary.not_started + summary.learning + summary.known;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex h-3 overflow-hidden rounded-full bg-muted">
        {STAGES.map((stage) => {
          const value = summary[stage.key];
          const pct = total > 0 ? (value / total) * 100 : 0;
          if (pct === 0) return null;
          return (
            <div
              key={stage.key}
              style={{ width: `${pct}%`, backgroundColor: stage.colorVar }}
              title={`${stage.label}: ${value}`}
            />
          );
        })}
      </div>
      <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
        {STAGES.map((stage) => (
          <span key={stage.key} className="inline-flex items-center gap-1.5">
            <span
              className="inline-block size-2.5 rounded-full"
              style={{ backgroundColor: stage.colorVar }}
            />
            {stage.label} ({summary[stage.key]})
          </span>
        ))}
        <span className="font-medium text-foreground">{Math.round(summary.known_rate)}% known</span>
      </div>
    </div>
  );
}
