import { ProjectCard } from "@/components/projects/ProjectCard";
import { ProjectDashboardEmptyState } from "@/components/projects/ProjectDashboardEmptyState";
import type { ProjectSnapshot } from "@/lib/project-meta";
import type { Project } from "@/types";

type ProjectGridProps = {
  projects: Project[];
  getSnapshot: (project: Project) => ProjectSnapshot;
  activeProjectId: string | null;
  onSelectProject: (project: Project) => void;
  onCreateProject: () => void;
};

export function ProjectGrid({
  projects,
  getSnapshot,
  activeProjectId,
  onSelectProject,
  onCreateProject,
}: ProjectGridProps) {
  if (projects.length === 0) {
    return <ProjectDashboardEmptyState onCreateProject={onCreateProject} />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          snapshot={getSnapshot(project)}
          selected={project.id === activeProjectId}
          onSelect={onSelectProject}
        />
      ))}
    </div>
  );
}
