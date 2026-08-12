import type { Metadata } from "next";
import { AdminSetsView } from "@/components/admin/admin-sets-view";

export const metadata: Metadata = { title: "Sets — Admin — Soulee" };

export default function AdminSetsPage() {
  return <AdminSetsView />;
}
