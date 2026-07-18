import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronRight, Folder, FileText, Search } from "lucide-react";
import { fileTree, type FileNode } from "@/lib/mock-workspace";

function TreeItem({
  node,
  depth,
  selected,
  onSelect,
  query,
}: {
  node: FileNode;
  depth: number;
  selected: string | null;
  onSelect: (n: FileNode) => void;
  query: string;
}) {
  const [open, setOpen] = useState(depth < 1);
  const isFolder = node.kind === "folder";
  const isSelected = selected === node.name;
  const match = !query || node.name.toLowerCase().includes(query.toLowerCase());

  if (!match && !node.children?.some((c) => c.name.toLowerCase().includes(query.toLowerCase()))) return null;

  return (
    <div>
      <button
        onClick={() => {
          if (isFolder) setOpen((v) => !v);
          onSelect(node);
        }}
        className={`w-full flex items-center gap-1.5 py-1 pr-2 rounded-md text-[13px] transition group ${
          isSelected ? "bg-oxblood/[0.08] text-oxblood" : "text-mulberry/80 hover:bg-oxblood/[0.04] hover:text-oxblood"
        }`}
        style={{ paddingLeft: 8 + depth * 14 }}
      >
        {isFolder ? (
          <ChevronRight
            size={12}
            className={`shrink-0 transition-transform text-mulberry/50 ${open ? "rotate-90" : ""}`}
          />
        ) : (
          <span className="w-3" />
        )}
        {isFolder ? (
          <Folder size={13} className="shrink-0 text-terracotta" />
        ) : (
          <FileText size={13} className="shrink-0 text-mulberry/50" />
        )}
        <span className="truncate font-mono text-[12.5px]">{node.name}</span>
      </button>
      <AnimatePresence initial={false}>
        {isFolder && open && node.children && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {node.children.map((child) => (
              <TreeItem key={child.name} node={child} depth={depth + 1} selected={selected} onSelect={onSelect} query={query} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function ExplorerPanel({ onSelect, selectedName }: { onSelect: (n: FileNode) => void; selectedName: string | null }) {
  const [q, setQ] = useState("");
  return (
    <div className="max-w-3xl mx-auto px-10 py-10">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
      <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Repository Explorer</h1>
      <p className="mt-2 text-[14px] text-mulberry/70 max-w-xl">
        Every folder is annotated. Select one to see its purpose, its neighbours, and a suggested way to read it.
      </p>

      <div className="mt-6 acrylic p-2 flex items-center gap-2">
        <Search size={14} className="ml-2 text-mulberry/55" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search folders and files…"
          className="flex-1 bg-transparent outline-none text-[13px] py-1.5 text-oxblood placeholder:text-mulberry/45"
        />
      </div>

      <div className="mt-4 acrylic p-3">
        <TreeItem node={fileTree} depth={0} selected={selectedName} onSelect={onSelect} query={q} />
      </div>
    </div>
  );
}
