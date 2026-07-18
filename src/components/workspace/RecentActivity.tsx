import { motion } from "motion/react";
import { BookOpen, FolderOpen, Pin, Search, Sparkles } from "lucide-react";
import type { Activity } from "@/lib/mock-repositories";

const icon = {
  opened: FolderOpen,
  generated: Sparkles,
  viewed: BookOpen,
  searched: Search,
  pinned: Pin,
} as const;

export function RecentActivity({ items }: { items: Activity[] }) {
  return (
    <ol className="relative pl-6">
      <div className="absolute left-[11px] top-2 bottom-2 w-px bg-gradient-to-b from-oxblood/25 via-oxblood/10 to-transparent" />
      {items.map((a, i) => {
        const Icon = icon[a.kind];
        return (
          <motion.li
            key={a.id}
            initial={{ opacity: 0, x: -8 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.06 }}
            className="relative py-3 flex items-start gap-3"
          >
            <div className="absolute -left-6 top-3 w-6 h-6 rounded-full bg-[rgba(255,248,228,0.95)] border border-oxblood/15 flex items-center justify-center text-oxblood">
              <Icon size={12} />
            </div>
            <div className="flex-1 flex items-baseline justify-between gap-3">
              <div>
                <div className="text-[13.5px] text-oxblood">{a.title}</div>
                <div className="text-[11.5px] font-mono text-mulberry/60">{a.context}</div>
              </div>
              <div className="text-[11px] text-mulberry/55 shrink-0">{a.time}</div>
            </div>
          </motion.li>
        );
      })}
    </ol>
  );
}
