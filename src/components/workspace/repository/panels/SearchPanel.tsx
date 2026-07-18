import { useMemo, useState } from "react";
import { motion } from "motion/react";
import { Search, FileText, Folder, Boxes, Code } from "lucide-react";

type Kind = "file" | "folder" | "function" | "component" | "dep" | "route";
type Result = { id: string; label: string; kind: Kind; context: string };

const corpus: Result[] = [
  { id: "1", label: "auth.ts", kind: "file", context: "src/services · JWT validation and session lifecycle" },
  { id: "2", label: "middleware.ts", kind: "file", context: "src · Route guards for protected pages" },
  { id: "3", label: "login.tsx", kind: "component", context: "src/pages · Renders the sign-in form" },
  { id: "4", label: "services", kind: "folder", context: "src · All API and auth communication" },
  { id: "5", label: "useAuth", kind: "function", context: "src/hooks/useAuth.ts · Reads current user context" },
  { id: "6", label: "TanStack Query", kind: "dep", context: "Server-state cache. React-friendly async layer." },
  { id: "7", label: "/dashboard", kind: "route", context: "Protected. Requires authenticated user." },
  { id: "8", label: "Dashboard.tsx", kind: "component", context: "src/components · Largest component in the tree" },
  { id: "9", label: "cn", kind: "function", context: "src/utils/cn.ts · Class-name merge helper" },
];

const iconFor: Record<Kind, typeof FileText> = {
  file: FileText,
  folder: Folder,
  component: Code,
  function: Code,
  dep: Boxes,
  route: Code,
};

export function SearchPanel({ onSelect }: { onSelect: (r: Result) => void }) {
  const [q, setQ] = useState("JWT");
  const results = useMemo(() => {
    if (!q) return corpus;
    const s = q.toLowerCase();
    return corpus.filter(
      (r) => r.label.toLowerCase().includes(s) || r.context.toLowerCase().includes(s) || r.kind.includes(s)
    );
  }, [q]);

  return (
    <div className="max-w-3xl mx-auto px-10 py-14">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55 text-center">Search</div>
      <div className="mt-3 acrylic-strong p-3 flex items-center gap-3">
        <Search size={18} className="ml-2 text-mulberry/60" />
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Files, folders, functions, components, dependencies, routes…"
          className="flex-1 bg-transparent outline-none font-serif text-[26px] text-oxblood placeholder:text-mulberry/40 py-2"
        />
        <kbd className="text-[10.5px] font-mono px-1.5 py-0.5 rounded bg-oxblood/5 text-mulberry/60 border border-oxblood/10">esc</kbd>
      </div>

      <div className="mt-3 text-[11.5px] font-mono uppercase tracking-wider text-mulberry/55 px-2">
        {results.length} result{results.length === 1 ? "" : "s"}
      </div>
      <div className="mt-2 space-y-1">
        {results.map((r, i) => {
          const Icon = iconFor[r.kind];
          return (
            <motion.button
              key={r.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: i * 0.02 }}
              onClick={() => onSelect(r)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-oxblood/[0.05] transition text-left group"
            >
              <div className="w-8 h-8 rounded-md bg-oxblood/[0.06] border border-oxblood/10 flex items-center justify-center">
                <Icon size={14} className="text-oxblood" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[13.5px] text-oxblood font-medium truncate">{r.label}</div>
                <div className="text-[12px] text-mulberry/65 truncate">{r.context}</div>
              </div>
              <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/50">{r.kind}</div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

export type SearchResult = Result;
