import type { components } from "@repo/types";

type SessionListItem = components["schemas"]["SessionListItem"];

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function SessionsHistoryTable({ sessions }: { sessions: SessionListItem[] }) {
  if (sessions.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No sessions yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground">
            <th className="px-3 py-2">Set</th>
            <th className="px-3 py-2">Mode</th>
            <th className="px-3 py-2">Date</th>
            <th className="px-3 py-2">Cards</th>
            <th className="px-3 py-2">Accuracy</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {sessions.map((session) => (
            <tr key={session.id} className="border-b border-border last:border-0">
              <td className="max-w-40 truncate px-3 py-2 font-normal text-foreground">
                {session.set_title}
              </td>
              <td className="px-3 py-2 capitalize text-muted-foreground">{session.mode}</td>
              <td className="px-3 py-2 text-muted-foreground">{formatDate(session.ended_at)}</td>
              <td className="px-3 py-2 text-muted-foreground">{session.cards_studied}</td>
              <td className="px-3 py-2 text-muted-foreground">{Math.round(session.accuracy)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
