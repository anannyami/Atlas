import { useState } from "react";
import { motion } from "motion/react";
import { archNodes, type ArchNode } from "@/lib/mock-workspace";
import { Plus, Minus, Locate } from "lucide-react";

export function ArchitecturePanel({
  selectedId,
  onSelect,
}: {
  selectedId: string | null;
  onSelect: (n: ArchNode) => void;
}) {
  const [hover, setHover] = useState<string | null>(null);
  const active = hover ?? selectedId;

  const isDim = (id: string) => {
    if (!active) return false;
    const node = archNodes.find((n) => n.id === active);
    if (!node) return false;
    return id !== active && !node.connections.includes(id) && !archNodes.some((n) => n.connections.includes(active) && n.id === id);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="px-10 pt-10 pb-4">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
        <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Architecture</h1>
        <p className="mt-2 text-[14px] text-mulberry/70 max-w-xl">
          A living map of how the pieces relate. Hover a node to see its neighbourhood; click to inspect it.
        </p>
      </div>

      <div className="relative flex-1 mx-10 mb-10 acrylic overflow-hidden">
        <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#792E3C" stopOpacity="0.35" />
              <stop offset="1" stopColor="#C7886B" stopOpacity="0.35" />
            </linearGradient>
          </defs>
          {archNodes.map((n) =>
            n.connections.map((cid) => {
              const t = archNodes.find((x) => x.id === cid);
              if (!t) return null;
              const key = `${n.id}-${cid}`;
              const active2 = active === n.id || active === cid;
              return (
                <path
                  key={key}
                  d={`M ${n.x} ${n.y} C ${n.x} ${(n.y + t.y) / 2}, ${t.x} ${(n.y + t.y) / 2}, ${t.x} ${t.y}`}
                  stroke={active2 ? "#792E3C" : "url(#edge)"}
                  strokeWidth={active2 ? 0.35 : 0.2}
                  fill="none"
                  style={{ transition: "all 0.25s", opacity: active && !active2 ? 0.15 : 1 }}
                  vectorEffect="non-scaling-stroke"
                />
              );
            })
          )}
        </svg>

        {archNodes.map((n) => {
          const isActive = active === n.id;
          const dim = isDim(n.id);
          return (
            <motion.button
              key={n.id}
              onMouseEnter={() => setHover(n.id)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onSelect(n)}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: dim ? 0.35 : 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className={`absolute -translate-x-1/2 -translate-y-1/2 px-4 py-2 rounded-xl text-[12.5px] font-medium border transition ${
                isActive
                  ? "bg-oxblood text-parchment border-oxblood shadow-[0_10px_30px_-8px_rgba(92,30,42,0.5)]"
                  : "bg-parchment/70 text-oxblood border-oxblood/15 hover:border-oxblood/40 backdrop-blur"
              }`}
              style={{ left: `${n.x}%`, top: `${n.y}%` }}
            >
              {n.label}
            </motion.button>
          );
        })}

        <div className="absolute bottom-4 right-4 flex flex-col gap-1.5">
          <button className="w-8 h-8 rounded-md bg-parchment/70 border border-oxblood/12 flex items-center justify-center text-mulberry hover:border-oxblood/30 transition"><Plus size={14} /></button>
          <button className="w-8 h-8 rounded-md bg-parchment/70 border border-oxblood/12 flex items-center justify-center text-mulberry hover:border-oxblood/30 transition"><Minus size={14} /></button>
          <button className="w-8 h-8 rounded-md bg-parchment/70 border border-oxblood/12 flex items-center justify-center text-mulberry hover:border-oxblood/30 transition"><Locate size={14} /></button>
        </div>

        <div className="absolute bottom-4 left-4 w-32 h-20 rounded-md bg-parchment/50 border border-oxblood/12 backdrop-blur p-1.5">
          <div className="relative w-full h-full">
            {archNodes.map((n) => (
              <div
                key={n.id}
                className="absolute w-1 h-1 rounded-full bg-oxblood/60"
                style={{ left: `${n.x}%`, top: `${n.y}%` }}
              />
            ))}
            <div className="absolute inset-0 border border-oxblood/25 rounded-sm" />
          </div>
        </div>
      </div>
    </div>
  );
}
