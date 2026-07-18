import { Link } from "@tanstack/react-router";
import { Search, Bell, Sun, ChevronDown, User } from "lucide-react";
import type { Repository } from "@/lib/mock-repositories";

function AtlasMark({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <defs>
        <linearGradient id="wtb-mark" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0" stopColor="#792E3C" />
          <stop offset="1" stopColor="#C7886B" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="14" stroke="url(#wtb-mark)" strokeWidth="1.5" />
      <path d="M16 2 C 22 10, 22 22, 16 30 M16 2 C 10 10, 10 22, 16 30 M2 16 H30" stroke="url(#wtb-mark)" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

export function WorkspaceTopBar({ repo }: { repo: Repository }) {
  return (
    <header className="h-14 shrink-0 border-b border-oxblood/10 bg-parchment/40 backdrop-blur-xl flex items-center gap-3 px-4">
      <Link to="/explore" className="flex items-center gap-2 pr-3 border-r border-oxblood/10">
        <AtlasMark size={20} />
        <span className="font-serif text-[16px] text-oxblood tracking-tight">Atlas</span>
      </Link>
      <button className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-md hover:bg-oxblood/5 transition group">
        <span className="text-[12px] font-mono uppercase tracking-wider text-mulberry/60">Repository</span>
        <span className="font-serif text-[15px] text-oxblood italic">{repo.owner}/{repo.name}</span>
        <ChevronDown size={13} className="text-mulberry/50 group-hover:text-oxblood transition" />
      </button>

      <div className="flex-1 flex justify-center">
        <div className="flex items-center gap-2 w-full max-w-lg px-3 py-1.5 rounded-lg bg-oxblood/[0.04] border border-oxblood/10 hover:border-oxblood/20 transition">
          <Search size={14} className="text-mulberry/60" />
          <input
            placeholder="Search files, folders, components…"
            className="flex-1 bg-transparent outline-none text-[13px] text-oxblood placeholder:text-mulberry/45"
          />
          <kbd className="text-[10.5px] font-mono px-1.5 py-0.5 rounded bg-oxblood/5 text-mulberry/60 border border-oxblood/10">⌘K</kbd>
        </div>
      </div>

      <button className="p-2 rounded-md hover:bg-oxblood/5 text-mulberry/70 transition" aria-label="Theme"><Sun size={15} /></button>
      <button className="p-2 rounded-md hover:bg-oxblood/5 text-mulberry/70 transition relative" aria-label="Notifications">
        <Bell size={15} />
        <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-burgundy" />
      </button>
      <div className="h-7 w-7 rounded-full bg-gradient-to-br from-[#C7886B] to-[#5C1E2A] text-parchment flex items-center justify-center text-[11px] font-medium ring-1 ring-oxblood/10">
        <User size={13} />
      </div>
    </header>
  );
}
