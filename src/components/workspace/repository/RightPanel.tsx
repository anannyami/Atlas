import { motion, AnimatePresence } from "motion/react";
import type { ReactNode } from "react";

export function RightPanel({ title, eyebrow, children, keyId }: { title: string; eyebrow?: string; children: ReactNode; keyId: string }) {
  return (
    <aside className="w-[340px] shrink-0 border-l border-oxblood/10 bg-parchment/30 backdrop-blur-xl overflow-y-auto">
      <AnimatePresence mode="wait">
        <motion.div
          key={keyId}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.22 }}
          className="p-6"
        >
          {eyebrow && (
            <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-2">{eyebrow}</div>
          )}
          <h3 className="font-serif text-[24px] text-oxblood leading-tight mb-5">{title}</h3>
          {children}
        </motion.div>
      </AnimatePresence>
    </aside>
  );
}

export function PanelBlock({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="mb-5">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-1.5">{label}</div>
      <div className="text-[13.5px] text-oxblood/85 leading-relaxed">{children}</div>
    </div>
  );
}

export function ReadingOrder({ steps }: { steps: string[] }) {
  return (
    <ol className="space-y-1.5">
      {steps.map((s, i) => (
        <li key={s} className="flex items-center gap-2.5">
          <span className="w-5 h-5 rounded-full bg-oxblood/[0.07] text-oxblood text-[10.5px] font-mono flex items-center justify-center border border-oxblood/10">
            {i + 1}
          </span>
          <code className="text-[12.5px] font-mono text-mulberry/85">{s}</code>
        </li>
      ))}
    </ol>
  );
}
