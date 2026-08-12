import { Ban, UserCheck, ShieldCheck, ShieldOff, KeyRound, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AdminUserListItem } from "@/lib/api/admin.api";

interface AdminUsersTableProps {
  users: AdminUserListItem[];
  isSelf: (user: AdminUserListItem) => boolean;
  onToggleActive: (user: AdminUserListItem) => void;
  onToggleRole: (user: AdminUserListItem) => void;
  onResetPassword: (user: AdminUserListItem) => void;
  onDelete: (user: AdminUserListItem) => void;
}

export function AdminUsersTable({
  users,
  isSelf,
  onToggleActive,
  onToggleRole,
  onResetPassword,
  onDelete,
}: AdminUsersTableProps) {
  if (users.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No users found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground">
            <th className="px-3 py-2">User</th>
            <th className="px-3 py-2">Role</th>
            <th className="px-3 py-2">Status</th>
            <th className="px-3 py-2">Streak</th>
            <th className="px-3 py-2">Sets</th>
            <th className="px-3 py-2">Sessions</th>
            <th className="px-3 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {users.map((user) => {
            const self = isSelf(user);
            return (
              <tr key={user.id} className="border-b border-border last:border-0">
                <td className="max-w-48 px-3 py-2">
                  <p className="truncate font-medium text-foreground">{user.display_name}</p>
                  <p className="truncate text-xs text-muted-foreground">{user.email}</p>
                </td>
                <td className="px-3 py-2">
                  <Badge variant={user.role === "admin" ? "default" : "outline"}>{user.role}</Badge>
                </td>
                <td className="px-3 py-2">
                  <Badge variant={user.is_active ? "secondary" : "destructive"}>
                    {user.is_active ? "active" : "banned"}
                  </Badge>
                </td>
                <td className="px-3 py-2 text-muted-foreground">{user.streak}</td>
                <td className="px-3 py-2 text-muted-foreground">{user.total_sets}</td>
                <td className="px-3 py-2 text-muted-foreground">{user.total_sessions}</td>
                <td className="px-3 py-2">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={user.is_active ? "Ban user" : "Unban user"}
                      disabled={self}
                      onClick={() => onToggleActive(user)}
                    >
                      {user.is_active ? <Ban className="size-3.5" /> : <UserCheck className="size-3.5" />}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={user.role === "admin" ? "Revoke admin" : "Make admin"}
                      disabled={self}
                      onClick={() => onToggleRole(user)}
                    >
                      {user.role === "admin" ? (
                        <ShieldOff className="size-3.5" />
                      ) : (
                        <ShieldCheck className="size-3.5" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Reset password"
                      onClick={() => onResetPassword(user)}
                    >
                      <KeyRound className="size-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Delete user"
                      disabled={self}
                      onClick={() => onDelete(user)}
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
