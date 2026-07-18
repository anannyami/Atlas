import { motion } from "motion/react";
import { insights, type Insight } from "@/lib/mock-workspace";

export function InsightsPanel({ onSelect }: { onSelect: (i: Insight) => void }) {
  return (
    <div className="max-w-4xl mx-auto px-10 py-10">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
      <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Insights</h1>
      <p className="mt-2 text-[14px] text-mulberry/70 max-w-xl">
        Observations designed to teach you something about this codebase, not to alarm you.
      </p>

      <div className="mt-8 space-y-3">
        {insights.map((it, i) => (
          <motion.button
            key={it.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
            onClick={() => onSelect(it)}
            className="w-full text-left acrylic p-6 hover:border-oxblood/25 transition group"
          >
            <div className="flex items-center gap-3">
              <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55">Observation {i + 1}</div>
              <div className="h-px flex-1 bg-oxblood/10" />
            </div>
            <div className="mt-2 font-serif text-[24px] text-oxblood leading-tight">{it.headline}</div>
            <div className="mt-2 text-[13.5px] text-mulberry/75">{it.detail}</div>
            <div className="mt-3 pt-3 border-t border-oxblood/10 text-[12.5px] text-mulberry/70">
              <span className="text-oxblood font-medium">Recommendation — </span>{it.recommendation}
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
