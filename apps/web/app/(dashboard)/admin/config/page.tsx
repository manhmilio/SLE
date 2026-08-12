import type { Metadata } from "next";
import { AdminConfigView } from "@/components/admin/admin-config-view";

export const metadata: Metadata = { title: "Config — Admin — Soulee" };

export default function AdminConfigPage() {
  return <AdminConfigView />;
}
