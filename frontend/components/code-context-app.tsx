"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { RepositoryAskSection } from "@/components/assistant/repository-ask-section";
import { ProjectGrid } from "@/components/projects/ProjectGrid";
import { ProjectOverview } from "@/components/projects/ProjectOverview";
import {
  RepositoryUploader,
  type IngestSuccess,
} from "@/components/repository/repository-uploader";
import { FileBrowser } from "@/components/repository/file-browser";
import { RepositorySearchSection } from "@/components/search/repository-search-section";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  createProject,
  fetchCurrentUser,
  listProjectFiles,
  listProjects,
} from "@/lib/api";
import { clearAccessToken, getAccessToken } from "@/lib/auth-token";
import { cn } from "@/lib/cn";
import {
  snapshotFromProject,
  type ImportSourceType,
  type ProjectSnapshot,
} from "@/lib/project-meta";
import type { FileRecord, Project, User } from "@/types";

type WorkspaceMode = "search" | "ask";

function createImportTypeMap(): Record<string, Set<ImportSourceType>> {
  return {};
}

export function CodeContextApp() {
  const router = useRouter();
  const [authReady, setAuthReady] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [importTypesByProject, setImportTypesByProject] = useState<
    Record<string, Set<ImportSourceType>>
  >(createImportTypeMap);
  const [lastIngestStatus, setLastIngestStatus] = useState<string>("pending");
  const [newProjectName, setNewProjectName] = useState("");
  const [showNewProjectForm, setShowNewProjectForm] = useState(false);
  const [creatingProject, setCreatingProject] = useState(false);
  const [searchSession, setSearchSession] = useState(0);
  const [askSession, setAskSession] = useState(0);
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("search");
  const [loadError, setLoadError] = useState<string | null>(null);

  const getProjectSnapshot = useCallback(
    (project: Project): ProjectSnapshot =>
      snapshotFromProject(project, {
        files: activeProject?.id === project.id ? files : [],
        importTypes: importTypesByProject[project.id] ?? [],
        lastIngestStatus:
          activeProject?.id === project.id ? lastIngestStatus : undefined,
      }),
    [activeProject, files, importTypesByProject, lastIngestStatus],
  );

  const activeSnapshot = useMemo(() => {
    if (!activeProject) return null;
    return getProjectSnapshot(activeProject);
  }, [activeProject, getProjectSnapshot]);

  const refreshProjects = useCallback(async () => {
    const userProjects = await listProjects();
    setProjects(userProjects);
    setActiveProject((current) => {
      if (!current) return null;
      return userProjects.find((project) => project.id === current.id) ?? current;
    });
  }, []);

  const loadProjectFiles = useCallback(async (project: Project) => {
    const projectFiles = await listProjectFiles(project.id);
    setFiles(projectFiles);
  }, []);

  const bootstrap = useCallback(async () => {
    if (!getAccessToken()) {
      router.replace("/login");
      return;
    }

    try {
      const currentUser = await fetchCurrentUser();
      const userProjects = await listProjects();
      setUser(currentUser);
      setProjects(userProjects);
      setLoadError(null);
    } catch {
      clearAccessToken();
      router.replace("/login");
      return;
    } finally {
      setAuthReady(true);
    }
  }, [router]);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  useEffect(() => {
    if (!activeProject) {
      setFiles([]);
      return;
    }
    void loadProjectFiles(activeProject).catch((err: unknown) => {
      setLoadError(err instanceof Error ? err.message : "Could not load project files.");
    });
  }, [activeProject, loadProjectFiles]);

  function handleSelectProject(project: Project) {
    setActiveProject(project);
    setLastIngestStatus(project.stats.file_count > 0 ? "indexed" : "pending");
    setLoadError(null);
  }

  function handleIngestSuccess(result: IngestSuccess) {
    if (!activeProject) return;

    setFiles(result.files);
    setLastIngestStatus(result.upload.ingestion_status);
    setImportTypesByProject((current) => {
      const importTypes = new Set(current[activeProject.id] ?? []);
      importTypes.add(result.sourceType);
      return { ...current, [activeProject.id]: importTypes };
    });
    void refreshProjects().catch((err: unknown) => {
      setLoadError(err instanceof Error ? err.message : "Could not refresh project stats.");
    });
    setSearchSession((value) => value + 1);
    setAskSession((value) => value + 1);
  }

  async function handleCreateProject() {
    const name = newProjectName.trim();
    if (!name || creatingProject) return;

    setCreatingProject(true);
    setLoadError(null);

    try {
      const project = await createProject(name);
      setProjects((current) => [project, ...current]);
      setActiveProject(project);
      setNewProjectName("");
      setShowNewProjectForm(false);
      setFiles([]);
      setLastIngestStatus("pending");
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Could not create project.");
    } finally {
      setCreatingProject(false);
    }
  }

  function handleLogout() {
    clearAccessToken();
    router.replace("/login");
  }

  if (!authReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-sm text-muted">
        Loading…
      </div>
    );
  }

  const projectIndexed =
    activeProject !== null && activeProject.stats.file_count > 0;

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <div className="brand-mark flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold">
              CC
            </div>
            <div className="min-w-0">
              <p className="brand-wordmark truncate text-sm">CodeContext</p>
              <p className="truncate text-xs text-muted-foreground">
                {user?.email ?? "Signed in"}
              </p>
            </div>
          </div>
          <Button type="button" variant="secondary" size="sm" onClick={handleLogout}>
            Log out
          </Button>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <section className="mb-8 border-b border-border-subtle pb-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-2xl">
              <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
                CodeContext
              </h1>
              <p className="mt-2 text-sm leading-relaxed text-muted sm:text-[0.9375rem]">
                AI Workspace for Code &amp; Documents
              </p>
            </div>
            <Button
              type="button"
              variant="primary"
              className="h-10 shrink-0"
              onClick={() => setShowNewProjectForm((value) => !value)}
            >
              + New Project
            </Button>
          </div>

          {showNewProjectForm ? (
            <Card className="mt-5 shadow-sm">
              <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-end sm:p-5">
                <div className="min-w-0 flex-1">
                  <label htmlFor="new-project-name" className="text-sm font-medium text-foreground">
                    Project name
                  </label>
                  <input
                    id="new-project-name"
                    value={newProjectName}
                    onChange={(event) => setNewProjectName(event.target.value)}
                    placeholder="Finance Tracker"
                    className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm"
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        void handleCreateProject();
                      }
                    }}
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="h-10"
                    onClick={() => {
                      setShowNewProjectForm(false);
                      setNewProjectName("");
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="button"
                    variant="primary"
                    className="h-10"
                    disabled={creatingProject || !newProjectName.trim()}
                    onClick={() => void handleCreateProject()}
                  >
                    {creatingProject ? "Creating…" : "Create project"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : null}

          <div className="mt-8">
            <p className="section-label">Projects</p>
            <p className="section-title mt-1">Your workspaces</p>
            <p className="mt-1 max-w-xl text-sm text-muted">
              Select a project to import sources, browse files, and run Search or Explain.
            </p>
            <div className="mt-5">
              <ProjectGrid
                projects={projects}
                getSnapshot={getProjectSnapshot}
                activeProjectId={activeProject?.id ?? null}
                onSelectProject={handleSelectProject}
                onCreateProject={() => setShowNewProjectForm(true)}
              />
            </div>
          </div>

          {loadError ? (
            <p className="status-banner-error mt-4 text-sm" role="alert">
              {loadError}
            </p>
          ) : null}
        </section>

        <section aria-labelledby="selected-project-heading" className="panel mb-8 p-5 sm:p-6 lg:p-7">
          <p id="selected-project-heading" className="section-label">
            Selected Project
          </p>
          <p className="section-title mt-1">
            {activeProject ? activeProject.name : "No project selected"}
          </p>

          {!activeProject ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">
                Choose a project card above to open its workspace.
              </p>
            </div>
          ) : activeSnapshot ? (
            <div className="mt-6">
              <ProjectOverview project={activeProject} snapshot={activeSnapshot} />
            </div>
          ) : null}
        </section>

        <section aria-labelledby="connect-heading" className="panel mb-8 p-5 sm:p-6 lg:p-7">
          <div className="mb-5">
            <p id="connect-heading" className="section-label">
              Import Sources
            </p>
            <p className="section-title mt-1">Add content to this project</p>
            <p className="mt-1 max-w-xl text-sm text-muted">
              Import Git repositories, ZIP archives, or individual files into the selected project.
            </p>
          </div>

          <RepositoryUploader
            projectId={activeProject?.id ?? ""}
            disabled={!activeProject}
            onSuccess={handleIngestSuccess}
          />

          {!activeProject ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">Select a project before importing sources.</p>
            </div>
          ) : !projectIndexed ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">
                No indexed content yet. Import a source to enable search and explain.
              </p>
            </div>
          ) : (
            <div className="mt-6 border-t border-border-subtle pt-6">
              <p className="section-label mb-3">Discovered files</p>
              {files.length > 0 ? (
                <FileBrowser files={files} />
              ) : (
                <p className="text-sm text-muted">Loading file list…</p>
              )}
            </div>
          )}
        </section>

        <section
          aria-labelledby="workspace-heading"
          className="panel flex min-h-[32rem] flex-col p-5 sm:p-6 lg:p-7"
        >
          <div className="mb-6 border-b border-border-subtle pb-5">
            <p id="workspace-heading" className="section-label">
              Project workspace
            </p>
            <p className="section-title mt-1">Search or explain</p>
            <div
              className="mt-4 flex w-full max-w-md rounded-lg border border-border bg-secondary-muted/70 p-1"
              role="tablist"
              aria-label="Workspace mode"
            >
              <button
                type="button"
                role="tab"
                id="workspace-tab-search"
                aria-selected={workspaceMode === "search"}
                aria-controls="workspace-panel-search"
                className={cn(
                  "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
                  workspaceMode === "search"
                    ? "bg-surface text-primary shadow-sm"
                    : "text-muted hover:text-foreground",
                )}
                onClick={() => setWorkspaceMode("search")}
              >
                🔍 Search
              </button>
              <button
                type="button"
                role="tab"
                id="workspace-tab-ask"
                aria-selected={workspaceMode === "ask"}
                aria-controls="workspace-panel-ask"
                className={cn(
                  "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
                  workspaceMode === "ask"
                    ? "bg-surface text-primary shadow-sm"
                    : "text-muted hover:text-foreground",
                )}
                onClick={() => setWorkspaceMode("ask")}
              >
                🤖 Explain
              </button>
            </div>
          </div>

          <div className="flex min-h-0 flex-1 flex-col">
            <div
              id="workspace-panel-search"
              role="tabpanel"
              aria-labelledby="workspace-tab-search"
              hidden={workspaceMode !== "search"}
              className={cn(
                "flex min-h-[26rem] flex-1 flex-col",
                workspaceMode !== "search" && "hidden",
              )}
            >
              <RepositorySearchSection
                key={`search-${searchSession}`}
                projectId={activeProject?.id ?? ""}
                disabled={!projectIndexed}
              />
            </div>

            <div
              id="workspace-panel-ask"
              role="tabpanel"
              aria-labelledby="workspace-tab-ask"
              hidden={workspaceMode !== "ask"}
              className={cn(
                "flex min-h-[26rem] flex-1 flex-col",
                workspaceMode !== "ask" && "hidden",
              )}
            >
              <RepositoryAskSection
                key={`ask-${askSession}`}
                projectId={activeProject?.id ?? ""}
                disabled={!projectIndexed}
              />
            </div>
          </div>
        </section>

        <p className="mt-8 text-center text-sm text-muted">
          <Link href="/register" className="text-primary hover:underline">
            Create another account
          </Link>
        </p>
      </main>
    </div>
  );
}
