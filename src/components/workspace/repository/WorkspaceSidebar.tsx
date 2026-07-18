import { motion } from "motion/react";
import type { LucideIcon } from "lucide-react";
import {
  LayoutGrid,
  FolderTree,
  Network,
  Boxes,
  Layers,
  BookOpen,
  Sparkles,
  Search,
  Settings,
} from "lucide-react";
import type { WorkspaceSection } from "@/lib/mock-workspace";

const items: { id: WorkspaceSection; label: string; icon: LucideIcon }[] = [
  { id: "overview", label: "Overview", icon: LayoutGrid },
  { id: "explorer", label: "Repository Explorer", icon: FolderTree },
  { id: "architecture", label: "Architecture", icon: Network },
  { id: "dependencies", label: "Dependencies", icon: Boxes },
  { id: "tech", label: "Technology Stack", icon: Layers },
  { id: "docs", label: "Documentation", icon: BookOpen },
  { id: "insights", label: "Insights", icon: Sparkles },
  { id: "search", label: "Search", icon: Search },
  { id: "settings", label: "Settings", icon: Settings },
];

export function WorkspaceSidebar({
  active,
  onChange,
}: {
  active: WorkspaceSection;
  onChange: (id: WorkspaceSection) => void;
}) {
  return (
    <aside className="w-60 shrink-0 border-r border-oxblood/10 bg-parchment/30 backdrop-blur-xl flex flex-col">
      <div className="px-4 pt-5 pb-3">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55">Workspace</div>
      </div>
      <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
        {items.map((it) => {
          const isActive = it.id === active;
          return (
            <button
              key={it.id}
              onClick={() => onChange(it.id)}
              className="w-full relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] transition group"
            >
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-lg bg-oxblood/[0.08] border border-oxblood/10"
                  transition={{ type: "spring", stiffness: 400, damping: 34 }}
                />
              )}
              <it.icon
                size={15}
                className={`relative z-10 transition ${isActive ? "text-oxblood" : "text-mulberry/55 group-hover:text-oxblood"}`}
              />
              <span
                className={`relative z-10 transition ${isActive ? "text-oxblood font-medium" : "text-mulberry/75 group-hover:text-oxblood"}`}
              >
                {it.label}
              </span>
            </button>
          );
        })}
      </nav>
      <div className="px-4 py-4 border-t border-oxblood/10">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-1">Reading progress</div>
        <div className="h-1 rounded-full bg-oxblood/10 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-[#C7886B] to-[#792E3C]" style={{ width: "38%" }} />
        </div>
        <div className="mt-1.5 text-[11px] text-mulberry/60">3 of 8 areas explored</div>
      </div>
    </aside>
  );
}
