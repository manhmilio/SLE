import { Button } from "@/components/ui/button";

const QUALITY_LEVELS = [
  { value: 1, label: "Again" },
  { value: 2, label: "Hard" },
  { value: 3, label: "Good" },
  { value: 4, label: "Easy" },
  { value: 5, label: "Perfect" },
];

export function LearnQualityPicker({ onSelect }: { onSelect: (quality: number) => void }) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {QUALITY_LEVELS.map((level) => (
        <Button key={level.value} variant="outline" onClick={() => onSelect(level.value)}>
          {level.label}
        </Button>
      ))}
    </div>
  );
}
