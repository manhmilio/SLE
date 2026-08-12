import type { components } from "@repo/types";

type ModeStats = components["schemas"]["ModeStats"];

export function ModeBreakdownTable({ modes }: { modes: ModeStats[] }) {
  if (modes.length === 0) {
    return <p className="text-sm text-muted-foreground">No sessions for this set yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground">
            <th className="px-3 py-2">Mode</th>
            <th className="px-3 py-2">Sessions</th>
            <th className="px-3 py-2">Avg. accuracy</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {modes.map((mode) => (
            <tr key={mode.mode} className="border-b border-border last:border-0">
              <td className="px-3 py-2 capitalize text-foreground">{mode.mode}</td>
              <td className="px-3 py-2 text-muted-foreground">{mode.sessions}</td>
              <td className="px-3 py-2 text-muted-foreground">{Math.round(mode.avg_accuracy)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
