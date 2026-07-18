import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { WorkspaceTopBar } from "@/components/workspace/repository/WorkspaceTopBar";
import { WorkspaceSidebar } from "@/components/workspace/repository/WorkspaceSidebar";
import { RightPanel, PanelBlock, ReadingOrder } from "@/components/workspace/repository/RightPanel";
import { OverviewPanel } from "@/components/workspace/repository/panels/OverviewPanel";
import { ExplorerPanel } from "@/components/workspace/repository/panels/ExplorerPanel";
import { ArchitecturePanel } from "@/components/workspace/repository/panels/ArchitecturePanel";
import { DependenciesPanel } from "@/components/workspace/repository/panels/DependenciesPanel";
import { TechStackPanel } from "@/components/workspace/repository/panels/TechStackPanel";
import { DocumentationPanel } from "@/components/workspace/repository/panels/DocumentationPanel";
import { InsightsPanel } from "@/components/workspace/repository/panels/InsightsPanel";
import { SearchPanel, type SearchResult } from "@/components/workspace/repository/panels/SearchPanel";
import { SettingsPanel } from "@/components/workspace/repository/panels/SettingsPanel";
import {
  findRepository,
  readingOrder,
  type FileNode,
  type ArchNode,
  type Insight,
  type WorkspaceSection,
} from "@/lib/mock-workspace";

export const Route = createFileRoute("/repository/$id")({
  head: () => ({
    meta: [
      { title: "Repository — Atlas" },
      { name: "description", content: "A workspace for reading unfamiliar codebases." },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: RepositoryWorkspace,
});

type Selection =
  | { kind: "default" }
  | { kind: "node"; label: string }
  | { kind: "folder"; node: FileNode }
  | { kind: "arch"; node: ArchNode }
  | { kind: "dep"; label: string }
  | { kind: "tech"; label: string; why: string }
  | { kind: "insight"; item: Insight }
  | { kind: "search"; result: SearchResult };

function RepositoryWorkspace() {
  const { id } = Route.useParams();
  const repo = findRepository(id);
  const [section, setSection] = useState<WorkspaceSection>("overview");
  const [selection, setSelection] = useState<Selection>({ kind: "default" });

  const changeSection = (s: WorkspaceSection) => {
    setSection(s);
    setSelection({ kind: "default" });
  };

  const renderCenter = () => {
    switch (section) {
      case "overview":
        return <OverviewPanel repo={repo} onFocusNode={(label) => setSelection({ kind: "node", label })} />;
      case "explorer":
        return (
          <ExplorerPanel
            selectedName={selection.kind === "folder" ? selection.node.name : null}
            onSelect={(n) => setSelection({ kind: "folder", node: n })}
          />
        );
      case "architecture":
        return (
          <ArchitecturePanel
            selectedId={selection.kind === "arch" ? selection.node.id : null}
            onSelect={(n) => setSelection({ kind: "arch", node: n })}
          />
        );
      case "dependencies":
        return <DependenciesPanel onSelect={(label) => setSelection({ kind: "dep", label })} />;
      case "tech":
        return <TechStackPanel onSelect={(label, why) => setSelection({ kind: "tech", label, why })} />;
      case "docs":
        return <DocumentationPanel repo={repo} />;
      case "insights":
        return <InsightsPanel onSelect={(item) => setSelection({ kind: "insight", item })} />;
      case "search":
        return <SearchPanel onSelect={(result) => setSelection({ kind: "search", result })} />;
      case "settings":
        return <SettingsPanel />;
    }
  };

  const renderRight = () => {
    if (selection.kind === "folder") {
      const n = selection.node;
      return (
        <RightPanel keyId={`folder-${n.name}`} eyebrow="Folder" title={n.name}>
          {n.purpose && <PanelBlock label="Purpose">{n.purpose}</PanelBlock>}
          {n.files && (
            <PanelBlock label="Files">
              <ul className="space-y-0.5">
                {n.files.map((f) => (
                  <li key={f} className="font-mono text-[12.5px] text-mulberry/80">{f}</li>
                ))}
              </ul>
            </PanelBlock>
          )}
          {n.usedBy && (
            <PanelBlock label="Used by">
              <div className="flex flex-wrap gap-1.5">
                {n.usedBy.map((u) => (
                  <span key={u} className="px-2 py-0.5 rounded-full bg-oxblood/[0.06] border border-oxblood/10 text-[12px] text-oxblood">{u}</span>
                ))}
              </div>
            </PanelBlock>
          )}
          {n.complexity && <PanelBlock label="Complexity">{n.complexity}</PanelBlock>}
          {n.recommendation && <PanelBlock label="Recommendation">{n.recommendation}</PanelBlock>}
        </RightPanel>
      );
    }
    if (selection.kind === "arch") {
      const n = selection.node;
      return (
        <RightPanel keyId={`arch-${n.id}`} eyebrow="Node" title={n.label}>
          <PanelBlock label="Purpose">{n.purpose}</PanelBlock>
          <PanelBlock label="Connected to">
            <div className="flex flex-wrap gap-1.5">
              {n.connections.map((c) => (
                <span key={c} className="px-2 py-0.5 rounded-full bg-oxblood/[0.06] border border-oxblood/10 text-[12px] text-oxblood capitalize">{c}</span>
              ))}
            </div>
          </PanelBlock>
          <PanelBlock label="Related files">
            <ul className="space-y-0.5">
              {n.files.map((f) => (
                <li key={f} className="font-mono text-[12.5px] text-mulberry/80">{f}</li>
              ))}
            </ul>
          </PanelBlock>
        </RightPanel>
      );
    }
    if (selection.kind === "dep") {
      return (
        <RightPanel keyId={`dep-${selection.label}`} eyebrow="Dependency" title={selection.label}>
          <PanelBlock label="Role">Foundational to this project's runtime behaviour. Traced through the dependency chain to leaves.</PanelBlock>
          <PanelBlock label="Recommendation">Read this package's README before diving into files that import it.</PanelBlock>
        </RightPanel>
      );
    }
    if (selection.kind === "tech") {
      return (
        <RightPanel keyId={`tech-${selection.label}`} eyebrow="Technology" title={selection.label}>
          <PanelBlock label="Why it's here">{selection.why}</PanelBlock>
        </RightPanel>
      );
    }
    if (selection.kind === "insight") {
      const it = selection.item;
      return (
        <RightPanel keyId={`insight-${it.id}`} eyebrow="Observation" title={it.headline}>
          <PanelBlock label="Detail">{it.detail}</PanelBlock>
          <PanelBlock label="Recommendation">{it.recommendation}</PanelBlock>
        </RightPanel>
      );
    }
    if (selection.kind === "search") {
      const r = selection.result;
      return (
        <RightPanel keyId={`search-${r.id}`} eyebrow={r.kind} title={r.label}>
          <PanelBlock label="Context">{r.context}</PanelBlock>
        </RightPanel>
      );
    }
    if (selection.kind === "node") {
      return (
        <RightPanel keyId={`node-${selection.label}`} eyebrow="Layer" title={selection.label}>
          <PanelBlock label="Purpose">Part of {repo.name}'s project map — a layer in the reading order.</PanelBlock>
          <PanelBlock label="Suggested next step">Open Architecture to see how this layer connects to its neighbours.</PanelBlock>
        </RightPanel>
      );
    }
    return (
      <RightPanel keyId="default" eyebrow="Intelligence" title="Repository Summary">
        <PanelBlock label="Purpose">
          {repo.description}
        </PanelBlock>
        <PanelBlock label="Main technologies">
          <div className="flex flex-wrap gap-1.5">
            {repo.technologies.map((t) => (
              <span key={t} className="px-2 py-0.5 rounded-full bg-oxblood/[0.06] border border-oxblood/10 text-[12px] text-oxblood">{t}</span>
            ))}
          </div>
        </PanelBlock>
        <PanelBlock label="Architecture">
          {repo.architecture}. State is co-located with screens; anything shared is lifted into a hook or a service.
        </PanelBlock>
        <PanelBlock label="Recommended reading order">
          <ReadingOrder steps={readingOrder} />
        </PanelBlock>
      </RightPanel>
    );
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[#f6ecd6]">
      <WorkspaceTopBar repo={repo} />
      <div className="flex-1 flex min-h-0">
        <WorkspaceSidebar active={section} onChange={changeSection} />
        <main className="flex-1 min-w-0 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={section}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
              className="min-h-full"
            >
              {renderCenter()}
            </motion.div>
          </AnimatePresence>
        </main>
        {renderRight()}
      </div>
    </div>
  );
}
