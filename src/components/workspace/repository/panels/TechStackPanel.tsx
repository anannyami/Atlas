import { motion } from "motion/react";
import { techStack } from "@/lib/mock-workspace";

export function TechStackPanel({ onSelect }: { onSelect: (label: string, why: string) => void }) {
  return (
    <div className="max-w-4xl mx-auto px-10 py-10">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
      <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Technology Stack</h1>
      <p className="mt-2 text-[14px] text-mulberry/70 max-w-xl">
        Every choice explains itself. Hover a chip to see why it earned its place in this repository.
      </p>

      <div className="mt-8 space-y-6">
        {techStack.map((cat, ci) => (
          <motion.div
            key={cat.name}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: ci * 0.05 }}
          >
            <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-2">{cat.name}</div>
            <div className="flex flex-wrap gap-2">
              {cat.items.map((it) => (
                <button
                  key={it.name}
                  onClick={() => onSelect(it.name, it.why)}
                  className="group px-4 py-2.5 rounded-xl bg-parchment/50 border border-oxblood/12 hover:border-oxblood/30 hover:bg-parchment/70 transition text-left"
                >
                  <div className="text-[13.5px] text-oxblood font-medium">{it.name}</div>
                  <div className="text-[12px] text-mulberry/65 max-w-[240px] mt-0.5">{it.why}</div>
                </button>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
