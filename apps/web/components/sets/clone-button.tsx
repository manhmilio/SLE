"use client";

import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCloneSetController } from "@/controllers/sets/use-clone-set-controller";

export function CloneButton({ setId }: { setId: string }) {
  const { clone, isCloning } = useCloneSetController();

  return (
    <Button variant="outline" onClick={() => clone(setId)} disabled={isCloning}>
      <Copy className="size-4" />
      {isCloning ? "Cloning…" : "Clone"}
    </Button>
  );
}
