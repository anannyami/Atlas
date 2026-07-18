import { motion } from "motion/react";
import { observations } from "@/lib/mock-workspace";
import type { Repository } from "@/lib/mock-repositories";

const summaryRows = (repo: Repository) => [
  ["Framework", repo.framework],
  ["Language", repo.language],
  ["Architecture", repo.architecture.split("·")[0].trim()],
  ["Repository Size", repo.size],
  ["Files", repo.files.toLocaleString()],
  ["Folders", repo.folders.toLocaleString()],
  ["Main Entry", "src/index.ts"],
  ["Difficulty", repo.difficulty],
  ["Documentation", "Excellent"],
  ["Health", "91 / 100"],
];

const mapNodes = [
  "Frontend", "Router", "Pages", "Components", "Hooks", "Services", "API", "Utilities", "Configuration",
];

export function OverviewPanel({ repo, onFocusNode }: { repo: Repository; onFocusNode: (label: string) => void }) {
  return (
    <div className="max-w-4xl mx-auto px-10 py-10">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Repository</div>
        <h1 className="font-serif text-[52px] text-oxblood leading-[1.02] mt-1">
          {repo.name.charAt(0).toUpperCase() + repo.name.slice(1)} Repository
        </h1>
        <p className="mt-3 text-[15px] text-mulberry/75 max-w-2xl leading-relaxed">
          {repo.description}
        </p>
      </motion.div>

      <section className="mt-10">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-3">Repository Summary</div>
        <div className="acrylic p-1.5">
          <div className="grid grid-cols-2 md:grid-cols-3">
            {summaryRows(repo).map(([k, v], i) => (
              <div
                key={k}
                className={`px-4 py-3.5 border-oxblood/10 ${i % 3 !== 2 ? "md:border-r" : ""} ${i < summaryRows(repo).length - 3 ? "border-b" : ""}`}
              >
                <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/55">{k}</div>
                <div className="mt-1 text-[14.5px] text-oxblood font-medium">{v}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-10">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-3">Project Map</div>
        <div className="acrylic p-8">
          <div className="flex flex-col items-center gap-2.5">
            {mapNodes.map((node, i) => (
              <div key={node} className="flex flex-col items-center gap-2.5">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  onClick={() => onFocusNode(node)}
                  className="min-w-[220px] px-5 py-2.5 rounded-xl bg-parchment/50 border border-oxblood/12 text-[13.5px] text-oxblood font-medium hover:border-oxblood/30 hover:bg-parchment/70 transition text-center shadow-[inset_0_1px_0_rgba(255,255,255,0.5)]"
                >
                  {node}
                </motion.button>
                {i < mapNodes.length - 1 && (
                  <svg width="10" height="18" className="text-oxblood/30">
                    <line x1="5" y1="0" x2="5" y2="14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="2 2" />
                    <path d="M1 12 L5 18 L9 12" stroke="currentColor" strokeWidth="1.2" fill="none" />
                  </svg>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-10 pb-6">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-3">Repository Observations</div>
        <div className="space-y-2.5">
          {observations.map((o, i) => (
            <motion.div
              key={o.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.05 * i }}
              className="acrylic p-5 hover:border-oxblood/25 transition group"
            >
              <div className="flex items-start gap-4">
                <div className="w-7 h-7 shrink-0 rounded-full bg-oxblood/[0.06] border border-oxblood/10 flex items-center justify-center font-serif text-[13px] text-oxblood italic">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-serif text-[19px] text-oxblood">{o.title}</div>
                  <div className="mt-1 text-[13px] text-mulberry/75">{o.detail}</div>
                  <div className="mt-2 pt-2 border-t border-oxblood/8 text-[12.5px] text-mulberry/65 italic">
                    Why it matters — {o.why}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
