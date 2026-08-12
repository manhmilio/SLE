import type { Metadata } from "next";
import { FoldersView } from "@/components/folders/folders-view";

export const metadata: Metadata = { title: "Folders — Soulee" };

export default function FoldersPage() {
  return <FoldersView />;
}
