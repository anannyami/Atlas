import { useState } from "react";
import { motion } from "motion/react";
import { Search } from "lucide-react";

const filters = ["All", "JavaScript", "TypeScript", "Go", "C++", "Beginner", "Advanced"];

export function RepositorySearch({
  value,
  onChange,
  activeFilter,
  onFilter,
}: {
  value: string;
  onChange: (v: string) => void;
  activeFilter: string;
  onFilter: (v: string) => void;
}) {
  const [focused, setFocused] = useState(false);
  return (
    <div className="flex flex-col md:flex-row md:items-center gap-3">
      <motion.div
        animate={{
          boxShadow: focused
            ? "0 0 0 3px rgba(120,46,60,0.12)"
            : "0 0 0 0 rgba(120,46,60,0)",
        }}
        className="acrylic flex items-center gap-2 px-3 py-2 flex-1 min-w-0"
      >
        <Search size={15} className="text-mulberry/60" />
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search repositories, frameworks, languages…"
          className="flex-1 bg-transparent outline-none text-[13.5px] text-oxblood placeholder:text-mulberry/45 py-1"
        />
      </motion.div>
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => onFilter(f)}
            className={`px-3 py-1.5 rounded-full text-[12px] whitespace-nowrap transition border ${
              activeFilter === f
                ? "bg-oxblood text-parchment border-oxblood"
                : "bg-transparent text-mulberry/80 border-oxblood/15 hover:border-oxblood/30"
            }`}
          >
            {f}
          </button>
        ))}
      </div>
    </div>
  );
}
