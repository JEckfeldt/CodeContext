"use client";

import { CodeBlock } from "@/components/content/code-block";
import type { ImplementationMilestone } from "@/types";

type MilestoneCardProps = {
  milestone: ImplementationMilestone;
  index: number;
};

function FileList({ label, files }: { label: string; files: string[] }) {
  if (files.length === 0) {
    return (
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="mt-1 text-sm text-muted">None listed.</p>
      </div>
    );
  }

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <ul className="mt-2 space-y-1">
        {files.map((file) => (
          <li
            key={file}
            className="rounded-md border border-border-subtle bg-surface px-2 py-1 font-mono text-xs text-foreground"
          >
            {file}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function MilestoneCard({ milestone, index }: MilestoneCardProps) {
  return (
    <li className="rounded-md border border-border-subtle bg-secondary-muted/30 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Milestone {index}
      </p>
      <h4 className="mt-2 text-sm font-semibold text-foreground">{milestone.title}</h4>

      <div className="mt-4 space-y-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Objective
          </p>
          <p className="mt-1 text-sm leading-relaxed text-muted">{milestone.objective}</p>
        </div>

        <FileList label="Files to modify" files={milestone.files_to_modify} />
        <FileList label="Files to create" files={milestone.files_to_create} />

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Implementation details
          </p>
          <p className="mt-1 text-sm leading-relaxed text-muted">
            {milestone.implementation_details}
          </p>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Testing requirements
          </p>
          {milestone.testing_requirements.length > 0 ? (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted">
              {milestone.testing_requirements.map((requirement) => (
                <li key={requirement}>{requirement}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-1 text-sm text-muted">None listed.</p>
          )}
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Cursor prompt
          </p>
          <CodeBlock code={milestone.cursor_prompt} className="my-2" />
        </div>
      </div>
    </li>
  );
}
