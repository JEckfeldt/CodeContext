"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { RepositoryAskSection } from "@/components/assistant/repository-ask-section";
import {
  RepositoryUploader,
  type IngestSuccess,
} from "@/components/repository/repository-uploader";
import { FileBrowser } from "@/components/repository/file-browser";
import { RepositoryView } from "@/components/repository/repository-view";
import { RepositorySearchSection } from "@/components/search/repository-search-section";
import { Button } from "@/components/ui/button";
import {
  createProject,
  fetchCurrentUser,
  listProjectFiles,
  listProjects,
} from "@/lib/api";
import { clearAccessToken, getAccessToken } from "@/lib/auth-token";
import { cn } from "@/lib/cn";
import type { FileRecord, Project, User } from "@/types";

type WorkspaceMode = "search" | "ask";

export function CodeContextApp() {
  const router = useRouter();
  const [authReady, setAuthReady] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [lastIngestStatus, setLastIngestStatus] = useState<string>("pending");
  const [newProjectName, setNewProjectName] = useState("");
  const [creatingProject, setCreatingProject] = useState(false);
  const [searchSession, setSearchSession] = useState(0);
  const [askSession, setAskSession] = useState(0);
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("search");
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadProjectFiles = useCallback(async (projectId: string) => {
    const projectFiles = await listProjectFiles(projectId);
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
    void loadProjectFiles(activeProject.id).catch((err: unknown) => {
      setLoadError(err instanceof Error ? err.message : "Could not load project files.");
    });
  }, [activeProject, loadProjectFiles]);

  function handleIngestSuccess(result: IngestSuccess) {
    setFiles(result.files);
    setLastIngestStatus(result.upload.ingestion_status);
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

  const projectReady = activeProject !== null && files.length > 0;

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
        <div className="mb-8 max-w-2xl">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
            AI workspace for your project
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-muted sm:text-[0.9375rem]">
            Create a project, import sources, then search and explain across all indexed content.
          </p>
        </div>

        <section aria-labelledby="projects-heading" className="panel mb-8 p-5 sm:p-6 lg:p-7">
          <p id="projects-heading" className="section-label">
            Projects
          </p>
          <p className="section-title mt-1">Your workspaces</p>
          <p className="mt-1 max-w-xl text-sm text-muted">
            Each project can combine Git repos, ZIP archives, and individual files.
          </p>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
            <div className="min-w-[12rem] flex-1">
              <label htmlFor="project-select" className="text-sm font-medium text-foreground">
                Active project
              </label>
              <select
                id="project-select"
                value={activeProject?.id ?? ""}
                onChange={(event) => {
                  const project = projects.find((item) => item.id === event.target.value) ?? null;
                  setActiveProject(project);
                  setLastIngestStatus(project ? "pending" : "pending");
                }}
                className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm"
              >
                <option value="">Select a project…</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="min-w-[12rem] flex-1">
              <label htmlFor="new-project-name" className="text-sm font-medium text-foreground">
                New project
              </label>
              <input
                id="new-project-name"
                value={newProjectName}
                onChange={(event) => setNewProjectName(event.target.value)}
                placeholder="My Finance App"
                className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm"
              />
            </div>
            <Button
              type="button"
              variant="primary"
              className="h-10 w-full sm:w-auto"
              disabled={creatingProject || !newProjectName.trim()}
              onClick={() => void handleCreateProject()}
            >
              {creatingProject ? "Creating…" : "Create project"}
            </Button>
          </div>

          {loadError ? (
            <p className="status-banner-error mt-4 text-sm" role="alert">
              {loadError}
            </p>
          ) : null}
        </section>

        <section aria-labelledby="connect-heading" className="panel p-5 sm:p-6 lg:p-7">
          <div className="mb-5">
            <p id="connect-heading" className="section-label">
              Sources
            </p>
            <p className="section-title mt-1">Import content</p>
            <p className="mt-1 max-w-xl text-sm text-muted">
              Choose a project above, then add Git URLs, ZIP archives, or individual files.
            </p>
          </div>

          <RepositoryUploader
            projectId={activeProject?.id ?? ""}
            disabled={!activeProject}
            onSuccess={handleIngestSuccess}
          />

          {!activeProject ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">Create or select a project before importing sources.</p>
            </div>
          ) : !projectReady ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">
                No indexed content yet. Import a source to enable search and explain.
              </p>
            </div>
          ) : (
            <div className="mt-6 space-y-5 border-t border-border-subtle pt-6">
              <RepositoryView
                name={activeProject.name}
                ingestionStatus={lastIngestStatus}
                fileCount={files.length}
              />
              <div>
                <p className="section-label mb-3">Discovered files</p>
                <FileBrowser files={files} />
              </div>
            </div>
          )}
        </section>

        <section
          aria-labelledby="workspace-heading"
          className="panel mt-8 flex min-h-[32rem] flex-col p-5 sm:mt-10 sm:p-6 lg:p-7"
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
                disabled={!projectReady}
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
                disabled={!projectReady}
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
