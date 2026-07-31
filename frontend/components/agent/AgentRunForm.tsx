"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

export type AgentTaskTemplateOption = {
  value: string;
  label: string;
  description: string;
  disabled?: boolean;
};

export const AGENT_TASK_TEMPLATE_OPTIONS: AgentTaskTemplateOption[] = [
  {
    value: "architecture_review",
    label: "Architecture review",
    description: "Analyze layers, modules, entry points, and data flow.",
  },
  {
    value: "implementation_planning",
    label: "Implementation Planning",
    description:
      "Analyze the repository and generate an ordered implementation plan with executable Cursor milestones.",
  },
  {
    value: "security_review",
    label: "Security review",
    description: "Coming soon.",
    disabled: true,
  },
  {
    value: "explain_auth",
    label: "Explain authentication",
    description: "Coming soon.",
    disabled: true,
  },
  {
    value: "refactoring_roadmap",
    label: "Refactoring roadmap",
    description: "Coming soon.",
    disabled: true,
  },
];

type AgentRunFormProps = {
  goal: string;
  taskTemplate: string;
  loading: boolean;
  disabled?: boolean;
  onGoalChange: (value: string) => void;
  onTaskTemplateChange: (value: string) => void;
  onSubmit: () => void;
};

export function AgentRunForm({
  goal,
  taskTemplate,
  loading,
  disabled = false,
  onGoalChange,
  onTaskTemplateChange,
  onSubmit,
}: AgentRunFormProps) {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form onSubmit={handleSubmit} className="mt-auto pt-2">
      <div className="composer space-y-4">
        <div>
          <label htmlFor="agent-task-template" className="text-sm font-medium text-foreground">
            Task template
          </label>
          <select
            id="agent-task-template"
            value={taskTemplate}
            onChange={(event) => onTaskTemplateChange(event.target.value)}
            disabled={disabled || loading}
            className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm text-foreground outline-none disabled:cursor-not-allowed disabled:text-muted"
          >
            {AGENT_TASK_TEMPLATE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
                {option.disabled ? " (coming soon)" : ""}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-muted-foreground">
            {
              AGENT_TASK_TEMPLATE_OPTIONS.find((option) => option.value === taskTemplate)
                ?.description
            }
          </p>
        </div>

        <div>
          <label htmlFor="agent-goal" className="sr-only">
            Agent analysis goal
          </label>
          <textarea
            id="agent-goal"
            value={goal}
            onChange={(event) => onGoalChange(event.target.value)}
            placeholder={
              disabled
                ? "Import a project to run the analysis agent..."
                : "Describe what you want the agent to analyze, e.g. summarize architecture, trace auth flow, or review module boundaries..."
            }
            disabled={disabled || loading}
            rows={3}
            className={cn(
              "w-full min-w-0 resize-none rounded-md border border-border bg-surface px-3 py-2.5 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted sm:text-[0.9375rem]",
            )}
          />
        </div>

        <div className="flex flex-col gap-2 border-t border-border-subtle pt-3 sm:flex-row sm:justify-end">
          <Button
            type="submit"
            variant="brand"
            className="w-full sm:w-auto"
            disabled={disabled || loading || !goal.trim()}
          >
            {loading ? "Running agent…" : "Run agent"}
          </Button>
        </div>
      </div>
    </form>
  );
}
