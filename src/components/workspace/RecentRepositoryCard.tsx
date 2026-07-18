import { motion } from "motion/react";
import { Link } from "@tanstack/react-router";
import { Clock, Sparkles } from "lucide-react";
import type { RecentRepo } from "@/lib/mock-repositories";

function Ring({ pct, color }: { pct: number; color: string }) {
  const r = 22;
  const c = 2 * Math.PI * r;
  return (
    <svg width="56" height="56" viewBox="0 0 56 56">
      <circle cx="28" cy="28" r={r} stroke="rgba(92,30,42,0.12)" strokeWidth="4" fill="none" />
      <circle
        cx="28" cy="28" r={r}
        stroke={color} strokeWidth="4" fill="none" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={c * (1 - pct / 100)}
        transform="rotate(-90 28 28)"
      />
      <text x="28" y="31" textAnchor="middle" fontSize="11" fontFamily="JetBrains Mono, monospace" fill="#5C1E2A" fontWeight="500">
        {pct}%
      </text>
    </svg>
  );
}

export function RecentRepositoryCard({ repo, index = 0 }: { repo: RecentRepo; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.5 }}
      whileHover={{ y: -3 }}
      className="acrylic p-5 min-w-[320px] flex items-center gap-5"
    >
      <div className="w-14 h-14 rounded-2xl shrink-0" style={{ background: `linear-gradient(135deg, ${repo.accent[0]}, ${repo.accent[1]})`, boxShadow: "inset 0 1px 0 rgba(255,255,255,0.35)" }} />
      <div className="flex-1 min-w-0">
        <div className="text-[11px] font-mono text-mulberry/60 uppercase tracking-wider">{repo.owner}</div>
        <div className="font-serif text-xl text-oxblood truncate">{repo.name}</div>
        <div className="mt-2 flex items-center gap-3 text-[11.5px] text-mulberry/70">
          <span className="inline-flex items-center gap-1"><Clock size={11} /> {repo.lastOpened}</span>
          <span className="inline-flex items-center gap-1"><Sparkles size={11} /> {repo.insights} insights</span>
        </div>
        <div className="mt-2 flex items-center gap-3 text-[11px] text-mulberry/60">
          <span>Docs {repo.documentationPct}%</span>
          <div className="flex-1 h-1 rounded-full bg-oxblood/10 overflow-hidden">
            <div className="h-full rounded-full bg-gradient-to-r from-[#C7886B] to-[#792E3C]" style={{ width: `${repo.documentationPct}%` }} />
          </div>
        </div>
      </div>
      <div className="shrink-0 flex flex-col items-center gap-1">
        <Ring pct={repo.architecturePct} color="#792E3C" />
        <Link to="/repository/$id" params={{ id: repo.id }} className="text-[11.5px] text-oxblood hover:underline">
          Resume →
        </Link>
      </div>
    </motion.div>
  );
}
