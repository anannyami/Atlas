import { motion } from "motion/react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, Star } from "lucide-react";
import type { Repository } from "@/lib/mock-repositories";
import { RepositoryCover } from "./RepositoryGlyph";

const diffTone: Record<string, string> = {
  Beginner: "bg-[#F0E6B1]/70 text-oxblood",
  Intermediate: "bg-[#E5C89B]/80 text-oxblood",
  Advanced: "bg-[#C7886B]/70 text-parchment",
  Expert: "bg-[#792E3C] text-parchment",
};

export function RepositoryCard({ repo, index = 0 }: { repo: Repository; index?: number }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.5, ease: [0.2, 0.7, 0.2, 1] }}
      whileHover={{ y: -4 }}
      className="acrylic p-5 flex flex-col gap-4 group"
    >
      <div className="relative">
        <RepositoryCover repo={repo} className="h-40" />
        <span className={`absolute top-3 right-3 px-2.5 py-1 rounded-full text-[11px] font-medium tracking-wide ${diffTone[repo.difficulty]}`}>
          {repo.difficulty}
        </span>
      </div>

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-[11px] font-mono text-mulberry/60 uppercase tracking-wider">{repo.owner}</div>
          <h3 className="font-serif text-2xl text-oxblood leading-tight truncate">{repo.name}</h3>
        </div>
        <div className="flex items-center gap-1 text-[12px] text-mulberry/70 shrink-0">
          <Star size={13} className="fill-[#C7886B] text-[#C7886B]" />
          {repo.stars}
        </div>
      </div>

      <p className="text-[13.5px] leading-relaxed text-mulberry/80 line-clamp-3">{repo.description}</p>

      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-[12px]">
        <Meta label="Language" value={repo.language} />
        <Meta label="Framework" value={repo.framework} />
        <Meta label="Size" value={repo.size} />
        <Meta label="Est. time" value={repo.estimatedTime} />
        <Meta label="Architecture" value={repo.architecture} span />
      </dl>

      <div className="flex flex-wrap gap-1.5">
        {repo.technologies.map((t) => (
          <span key={t} className="px-2 py-0.5 rounded-full text-[11px] font-mono bg-oxblood/5 text-mulberry/80 border border-oxblood/10">
            {t}
          </span>
        ))}
      </div>

      <div className="mt-1 flex items-center gap-2">
        <Link
          to="/repository/$id"
          params={{ id: repo.id }}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-burgundy hover:bg-oxblood text-parchment text-[13px] font-medium transition"
          style={{ boxShadow: "inset 0 1px 0 rgba(240,230,177,0.2), 0 8px 20px -10px rgba(92,30,42,0.6)" }}
        >
          Explore <ArrowRight size={14} />
        </Link>
        <button className="px-4 py-2.5 rounded-xl text-[13px] font-medium text-oxblood border border-oxblood/15 hover:bg-oxblood/5 transition">
          View Details
        </button>
      </div>
    </motion.article>
  );
}

function Meta({ label, value, span }: { label: string; value: string; span?: boolean }) {
  return (
    <div className={span ? "col-span-2" : ""}>
      <dt className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/50">{label}</dt>
      <dd className="text-oxblood/90 truncate">{value}</dd>
    </div>
  );
}
