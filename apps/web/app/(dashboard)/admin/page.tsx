import type { Metadata } from "next";
import { AdminDashboardView } from "@/components/admin/admin-dashboard-view";

export const metadata: Metadata = { title: "Admin — Soulee" };

export default function AdminDashboardPage() {
  return <AdminDashboardView />;
}
