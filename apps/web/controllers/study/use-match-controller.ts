"use client";

import { useEffect, useRef, useState } from "react";
import { useStudySessionController } from "@/controllers/study/use-study-session-controller";

interface Tile {
  id: string;
  cardId: string;
  text: string;
  matched: boolean;
}

function shuffle<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/**
 * Match mode isn't index-sequential like the other three, so it wraps the base
 * session controller with its own tile-board state instead of reusing the
 * sequential controller.
 */
export function useMatchController(setId: string) {
  const session = useStudySessionController(setId, "match");
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [shakeIds, setShakeIds] = useState<string[]>([]);
  const finishedRef = useRef(false);

  useEffect(() => {
    session.start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (session.hasStarted && session.cards.length > 0 && tiles.length === 0) {
      const built = shuffle(
        session.cards.flatMap((card) => [
          { id: `${card.id}-front`, cardId: card.id, text: card.front, matched: false },
          { id: `${card.id}-back`, cardId: card.id, text: card.back, matched: false },
        ])
      );
      setTiles(built);
      session.markCardShown();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.hasStarted, session.cards]);

  const isEmpty = session.hasStarted && session.cards.length === 0;
  const isDone = tiles.length > 0 && tiles.every((tile) => tile.matched);

  useEffect(() => {
    if ((isEmpty || isDone) && !finishedRef.current) {
      finishedRef.current = true;
      session.finish();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEmpty, isDone]);

  function selectTile(tileId: string) {
    const tile = tiles.find((t) => t.id === tileId);
    if (!tile || tile.matched) return;

    if (!selectedId) {
      setSelectedId(tileId);
      return;
    }
    if (selectedId === tileId) {
      setSelectedId(null);
      return;
    }

    const first = tiles.find((t) => t.id === selectedId);
    if (!first) return;

    const isMatch = first.cardId === tile.cardId;

    if (isMatch) {
      session.submitAnswer({ cardId: first.cardId, isCorrect: true });
      setTiles((prev) => prev.map((t) => (t.cardId === first.cardId ? { ...t, matched: true } : t)));
    } else {
      session.submitAnswer({ cardId: first.cardId, isCorrect: false });
      session.submitAnswer({ cardId: tile.cardId, isCorrect: false });
      setShakeIds([first.id, tile.id]);
      setTimeout(() => setShakeIds([]), 400);
    }
    setSelectedId(null);
    session.markCardShown();
  }

  return {
    ...session,
    tiles,
    selectedId,
    shakeIds,
    selectTile,
    isEmpty,
    isDone,
  };
}
