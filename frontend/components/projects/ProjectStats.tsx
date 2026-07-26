import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/cn";

type ProjectStatItem = {
  label: string;
  value: string;
  hint?: string;
  placeholder?: boolean;
};

type ProjectStatsProps = {
  items: ProjectStatItem[];
};

export function ProjectStats({ items }: ProjectStatsProps) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {items.map((item) => (
        <Card key={item.label} className="shadow-sm">
          <CardContent className="p-4">
            <p className="section-label">{item.label}</p>
            <p
              className={cn(
                "mt-2 text-lg font-semibold tracking-tight text-foreground",
                item.placeholder && "text-muted-foreground",
              )}
            >
              {item.value}
            </p>
            {item.hint ? <p className="mt-1 text-xs text-muted-foreground">{item.hint}</p> : null}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
