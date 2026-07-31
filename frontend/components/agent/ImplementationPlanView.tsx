"use client";

import type { ReactNode } from "react";

import { MilestoneCard } from "@/components/agent/MilestoneCard";
import type { AffectedComponent, ImplementationPlanArtifact } from "@/types";

type ImplementationPlanViewProps = {
  plan: ImplementationPlanArtifact;
};

function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="mt-5 border-t border-border-subtle pt-5 first:mt-0 first:border-t-0 first:pt-0">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {title}
      </h4>
      <div className="mt-2">{children}</div>
    </section>
  );
}

function ComponentList({ components }: { components: AffectedComponent[] }) {
  if (components.length === 0) {
    return <p className="text-sm text-muted">No affected components listed.</p>;
  }

  return (
    <ul className="space-y-3">
      {components.map((component) => (
        <li
          key={component.name}
          className="rounded-md border border-border-subtle bg-secondary-muted/30 px-3 py-3"
        >
          <p className="text-sm font-medium text-foreground">{component.name}</p>
          <p className="mt-1 text-sm text-muted">{component.description}</p>
          {component.file_paths.length > 0 ? (
            <ul className="mt-2 space-y-1">
              {component.file_paths.map((path) => (
                <li
                  key={path}
                  className="font-mono text-xs text-muted-foreground"
                >
                  {path}
                </li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

export function ImplementationPlanView({ plan }: ImplementationPlanViewProps) {
  return (
    <div className="rounded-md border border-border bg-surface px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Implementation plan
      </p>
      <h3 className="mt-2 text-base font-semibold text-foreground">{plan.title}</h3>

      <Section title="Goal">
        <p className="text-sm leading-relaxed text-muted">{plan.goal}</p>
      </Section>

      <Section title="Executive summary">
        <p className="text-sm leading-relaxed text-muted">{plan.summary}</p>
      </Section>

      <Section title="Existing system analysis">
        <p className="text-sm leading-relaxed text-muted whitespace-pre-wrap">
          {plan.existing_system_analysis}
        </p>
      </Section>

      <Section title="Relevant files">
        {plan.relevant_files.length > 0 ? (
          <ul className="space-y-1">
            {plan.relevant_files.map((path) => (
              <li
                key={path}
                className="rounded-md border border-border-subtle bg-secondary-muted/20 px-2 py-1 font-mono text-xs text-foreground"
              >
                {path}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">No relevant files listed.</p>
        )}
      </Section>

      <Section title="Affected components">
        <ComponentList components={plan.affected_components} />
      </Section>

      <Section title="Risks">
        {plan.risks.length > 0 ? (
          <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
            {plan.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">No risks listed.</p>
        )}
      </Section>

      <Section title="Milestones">
        <ol className="space-y-4">
          {plan.milestones.map((milestone, index) => (
            <MilestoneCard
              key={`${milestone.title}-${index}`}
              milestone={milestone}
              index={index + 1}
            />
          ))}
        </ol>
      </Section>
    </div>
  );
}
