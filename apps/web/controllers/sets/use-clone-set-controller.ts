"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useCloneSetMutation } from "@/lib/mutations/set-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useCloneSetController() {
  const router = useRouter();
  const { mutate, isPending } = useCloneSetMutation();

  function clone(setId: string) {
    mutate(setId, {
      onSuccess: (cloned) => {
        toast.success("Set cloned to your library.");
        router.push(`/sets/${cloned.id}`);
      },
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't clone this set.")),
    });
  }

  return { clone, isCloning: isPending };
}
