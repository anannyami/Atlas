import { Link } from "@tanstack/react-router";
import { Search, Settings } from "lucide-react";

function AtlasMark({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <defs>
        <linearGradient id="ws-mark" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0" stopColor="#792E3C" />
          <stop offset="1" stopColor="#C7886B" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="14" stroke="url(#ws-mark)" strokeWidth="1.5" />
      <path d="M16 2 C 22 10, 22 22, 16 30 M16 2 C 10 10, 10 22, 16 30 M2 16 H30" stroke="url(#ws-mark)" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

export function WorkspaceHeader() {
  return (
    <div className="fixed top-0 left-0 right-0 z-40 flex justify-center px-6 pt-5">
      <nav className="acrylic flex items-center gap-2 pl-2 pr-2 py-2 rounded-full w-full max-w-5xl">
        <Link to="/" className="flex items-center gap-2 pl-3 pr-4 py-1.5">
          <AtlasMark />
          <span className="font-serif text-[17px] tracking-tight text-oxblood">Atlas</span>
        </Link>
        <div className="h-5 w-px bg-oxblood/15" />
        <div className="flex items-center gap-1 flex-1 min-w-0">
          <Link to="/explore" className="px-3.5 py-1.5 text-[13px] text-oxblood rounded-full bg-oxblood/5">
            Explore
          </Link>
          <a className="px-3.5 py-1.5 text-[13px] text-mulberry/70 hover:text-oxblood transition rounded-full hover:bg-oxblood/5 cursor-pointer">
            Library
          </a>
          <a className="px-3.5 py-1.5 text-[13px] text-mulberry/70 hover:text-oxblood transition rounded-full hover:bg-oxblood/5 cursor-pointer">
            Insights
          </a>
        </div>
        <button className="p-2 rounded-full hover:bg-oxblood/5 text-mulberry/80 transition" aria-label="Search">
          <Search size={16} />
        </button>
        <button className="p-2 rounded-full hover:bg-oxblood/5 text-mulberry/80 transition" aria-label="Settings">
          <Settings size={16} />
        </button>
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#C7886B] to-[#5C1E2A] text-parchment flex items-center justify-center text-[12px] font-medium ring-1 ring-oxblood/10">
          MK
        </div>
      </nav>
    </div>
  );
}
