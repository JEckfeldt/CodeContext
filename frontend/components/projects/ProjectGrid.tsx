import { ProjectCard } from "@/components/projects/ProjectCard";
import { emptyProjectSnapshot, type ProjectSnapshot } from "@/lib/project-meta";
import type { Project } from "@/types";

type ProjectGridProps = {
  projects: Project[];
  snapshots: Record<string, ProjectSnapshot>;
  activeProjectId: string | null;
  onSelectProject: (project: Project) => void;
};

export function ProjectGrid({
  projects,
  snapshots,
  activeProjectId,
  onSelectProject,
}: ProjectGridProps) {
  if (projects.length === 0) {
    return (
      <div className="status-banner">
        <p className="text-sm text-muted">
          No projects yet. Use <span className="font-medium text-foreground">+ New Project</span> to
          create your first workspace.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          snapshot={snapshots[project.id] ?? emptyProjectSnapshot()}
          selected={project.id === activeProjectId}
          onSelect={onSelectProject}
        />
      ))}
    </div>
  );
}
