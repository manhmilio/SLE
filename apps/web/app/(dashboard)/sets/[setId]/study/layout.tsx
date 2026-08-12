import Link from "next/link";
import { X } from "lucide-react";

export default async function StudyLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-end">
        <Link
          href={`/sets/${setId}`}
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <X className="size-4" />
          Exit
        </Link>
      </div>
      {children}
    </div>
  );
}
