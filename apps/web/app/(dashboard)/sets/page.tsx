import type { Metadata } from "next";
import { SetsView } from "@/components/sets/sets-view";

export const metadata: Metadata = { title: "Your sets — Soulee" };

export default function SetsPage() {
  return <SetsView />;
}
