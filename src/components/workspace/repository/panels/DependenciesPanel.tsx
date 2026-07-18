import { useState } from "react";
import { motion } from "motion/react";
import { dependencies } from "@/lib/mock-workspace";

export function DependenciesPanel({ onSelect }: { onSelect: (label: string) => void }) {
  const [hover, setHover] = useState<string | null>(null);

  const chain = (id: string): string[] => {
    const out = new Set<string>([id]);
    let cur = [id];
    while (cur.length) {
      const next: string[] = [];
      for (const c of cur) {
        for (const d of dependencies) {
          if (d.depends.includes(c) && !out.has(d.id)) {
            out.add(d.id);
            next.push(d.id);
          }
        }
        const node = dependencies.find((d) => d.id === c);
        node?.depends.forEach((x) => {
          if (!out.has(x)) { out.add(x); next.push(x); }
        });
      }
      cur = next;
    }
    return Array.from(out);
  };

  const highlighted = hover ? chain(hover) : null;

  return (
    <div className="max-w-3xl mx-auto px-10 py-10">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
      <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Dependencies</h1>
      <p className="mt-2 text-[14px] text-mulberry/70 max-w-xl">
        A vertical chain from foundation to leaf. Hover any package to trace what it touches and what it relies on.
      </p>

      <div className="mt-8 acrylic p-8">
        <div className="flex flex-col items-center gap-2.5">
          {dependencies.map((d, i) => {
            const dim = highlighted && !highlighted.includes(d.id);
            return (
              <div key={d.id} className="flex flex-col items-center gap-2.5 w-full">
                <motion.button
                  onMouseEnter={() => setHover(d.id)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => onSelect(d.label)}
                  animate={{ opacity: dim ? 0.3 : 1 }}
                  className={`w-full max-w-md px-5 py-3 rounded-xl text-left border transition ${
                    hover === d.id
                      ? "bg-oxblood text-parchment border-oxblood"
                      : "bg-parchment/50 text-oxblood border-oxblood/12 hover:border-oxblood/30"
                  }`}
                >
                  <div className="text-[14px] font-medium">{d.label}</div>
                  <div className={`text-[12px] mt-0.5 ${hover === d.id ? "text-parchment/80" : "text-mulberry/70"}`}>{d.role}</div>
                </motion.button>
                {i < dependencies.length - 1 && (
                  <svg width="10" height="18" className={dim ? "text-oxblood/10" : "text-oxblood/30"}>
                    <line x1="5" y1="0" x2="5" y2="14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="2 2" />
                    <path d="M1 12 L5 18 L9 12" stroke="currentColor" strokeWidth="1.2" fill="none" />
                  </svg>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
