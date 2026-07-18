import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence, useScroll, useTransform, useInView } from "motion/react";

export const Route = createFileRoute("/")({
  component: AtlasLanding,
});

/* ----------------------------- Living Background ---------------------------- */

function LivingBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 atlas-stage atlas-noise">
      <motion.div
        className="atlas-blob"
        style={{ width: 900, height: 900, top: "-20%", left: "-10%", background: "radial-gradient(circle, #F0E6B1, transparent 60%)" }}
        animate={{ x: [0, 60, -20, 0], y: [0, 40, -30, 0] }}
        transition={{ duration: 28, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="atlas-blob"
        style={{ width: 800, height: 800, top: "10%", right: "-15%", background: "radial-gradient(circle, #C7886B, transparent 65%)", opacity: 0.55 }}
        animate={{ x: [0, -50, 30, 0], y: [0, 60, 20, 0] }}
        transition={{ duration: 32, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="atlas-blob"
        style={{ width: 1000, height: 1000, bottom: "-25%", left: "20%", background: "radial-gradient(circle, #8E3E4D, transparent 60%)", opacity: 0.4 }}
        animate={{ x: [0, 40, -30, 0], y: [0, -30, 20, 0] }}
        transition={{ duration: 36, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="atlas-blob"
        style={{ width: 600, height: 600, bottom: "5%", right: "5%", background: "radial-gradient(circle, #5C1E2A, transparent 55%)", opacity: 0.3 }}
        animate={{ x: [0, -30, 20, 0], y: [0, 20, -40, 0] }}
        transition={{ duration: 40, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

/* --------------------------------- Nav --------------------------------- */

function AtlasMark({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <defs>
        <linearGradient id="atlas-mark" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0" stopColor="#792E3C" />
          <stop offset="1" stopColor="#C7886B" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="14" stroke="url(#atlas-mark)" strokeWidth="1.5" />
      <path d="M16 2 C 22 10, 22 22, 16 30 M16 2 C 10 10, 10 22, 16 30 M2 16 H30" stroke="url(#atlas-mark)" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

function Nav() {
  return (
    <div className="fixed top-0 left-0 right-0 z-40 flex justify-center px-6 pt-5">
      <nav className="acrylic flex items-center gap-1 px-2 py-2 rounded-full">
        <div className="flex items-center gap-2 pl-3 pr-4 py-1.5">
          <AtlasMark />
          <span className="font-serif text-[17px] tracking-tight text-oxblood">Atlas</span>
        </div>
        <div className="h-5 w-px bg-oxblood/15" />
        {["Documentation", "Features", "Demo"].map((l) => (
          <a key={l} href={`#${l.toLowerCase()}`} className="px-3.5 py-1.5 text-[13px] text-mulberry/80 hover:text-oxblood transition rounded-full hover:bg-oxblood/5">
            {l}
          </a>
        ))}
        <div className="h-5 w-px bg-oxblood/15" />
        <button className="px-4 py-1.5 text-[13px] font-medium text-parchment bg-burgundy hover:bg-oxblood transition rounded-full">
          Sign In
        </button>
      </nav>
    </div>
  );
}

/* ------------------------------- Hero ------------------------------- */

const MOCK = {
  name: "vercel/next.js",
  stars: "126.4k",
  language: "TypeScript",
  files: 4821,
  summary:
    "A React framework for the web with hybrid static & server rendering, file-system routing, API routes, and a rich runtime for building production applications.",
  tree: [
    { name: "packages", depth: 0, kind: "dir" },
    { name: "next", depth: 1, kind: "dir" },
    { name: "src", depth: 2, kind: "dir" },
    { name: "server", depth: 3, kind: "dir" },
    { name: "client", depth: 3, kind: "dir" },
    { name: "compiled", depth: 2, kind: "dir" },
    { name: "create-next-app", depth: 1, kind: "dir" },
    { name: "examples", depth: 0, kind: "dir" },
    { name: "docs", depth: 0, kind: "dir" },
    { name: "package.json", depth: 0, kind: "file" },
  ],
  deps: ["react", "react-dom", "webpack", "swc", "postcss", "styled-jsx", "acorn", "amphtml-validator"],
  nodes: [
    { id: "core", label: "Core", x: 50, y: 50, r: 34 },
    { id: "server", label: "Server", x: 20, y: 25, r: 22 },
    { id: "client", label: "Client", x: 80, y: 25, r: 22 },
    { id: "compiler", label: "Compiler", x: 22, y: 80, r: 20 },
    { id: "router", label: "Router", x: 78, y: 78, r: 20 },
    { id: "cli", label: "CLI", x: 50, y: 92, r: 14 },
  ],
  edges: [
    ["core", "server"], ["core", "client"], ["core", "compiler"], ["core", "router"],
    ["server", "router"], ["client", "router"], ["cli", "core"],
  ],
};

function Hero() {
  const [phase, setPhase] = useState<"idle" | "loading" | "revealed">("idle");
  const [value, setValue] = useState("https://github.com/vercel/next.js");

  const analyze = () => {
    if (phase !== "idle") return;
    setPhase("loading");
    setTimeout(() => setPhase("revealed"), 1400);
  };

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-28 pb-20">
      <motion.div
        layout
        transition={{ layout: { duration: 0.9, ease: [0.22, 1, 0.36, 1] } }}
        className="w-full max-w-6xl mx-auto flex flex-col items-center"
      >
        {/* Eyebrow */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.8 }}
          className="mb-8 flex items-center gap-2 px-4 py-1.5 rounded-full acrylic text-[12px] text-mulberry tracking-wide"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-burgundy animate-pulse" />
          A workspace for reading unfamiliar codebases
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          className="font-serif text-center text-[clamp(48px,8vw,112px)] leading-[0.95] text-oxblood"
        >
          Understand any codebase.
          <br />
          <span className="italic text-burgundy">Before you read a single file.</span>
        </motion.h1>

        {/* Input row */}
        <motion.div
          layout
          className="mt-14 w-full max-w-2xl"
        >
          <div className="acrylic-strong flex items-center gap-2 p-2 rounded-2xl">
            <div className="pl-4 text-mulberry/60">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
                <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.09.68-.22.68-.49v-1.7c-2.78.62-3.37-1.35-3.37-1.35-.45-1.17-1.11-1.48-1.11-1.48-.91-.63.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.27 2.75 1.05a9.4 9.4 0 0 1 5 0c1.91-1.32 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9v2.82c0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2z"/>
              </svg>
            </div>
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="https://github.com/owner/repository"
              className="flex-1 bg-transparent outline-none py-3 px-1 text-[15px] text-oxblood placeholder:text-mulberry/40 font-mono"
              onKeyDown={(e) => e.key === "Enter" && analyze()}
            />
            <motion.button
              onClick={analyze}
              whileTap={{ scale: 0.96 }}
              whileHover={{ scale: 1.02 }}
              className="relative px-6 py-3 rounded-xl bg-burgundy text-parchment text-[14px] font-medium tracking-wide overflow-hidden group"
              style={{
                boxShadow: "inset 0 1px 0 rgba(255,240,210,0.25), 0 8px 24px -8px rgba(92,30,42,0.5)",
              }}
            >
              <span className="relative z-10 flex items-center gap-2">
                {phase === "loading" ? (
                  <>
                    <motion.span
                      className="w-3.5 h-3.5 border-2 border-parchment/40 border-t-parchment rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                    />
                    Analyzing
                  </>
                ) : phase === "revealed" ? (
                  "Reset"
                ) : (
                  <>Analyze Repository →</>
                )}
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-transparent via-parchment/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
            </motion.button>
          </div>
          <p className="mt-3 text-center text-[12px] text-mulberry/60">
            Try it with any public repository — no sign-in required.
          </p>
        </motion.div>

        {/* Revealed product */}
        <AnimatePresence>
          {phase === "revealed" && (
            <motion.div
              key="revealed"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              className="mt-12 w-full grid grid-cols-12 gap-4"
            >
              {/* Repository card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="col-span-12 acrylic-strong p-5 rounded-2xl flex flex-wrap items-center gap-6"
              >
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-terracotta to-burgundy flex items-center justify-center text-parchment font-serif text-xl">n</div>
                  <div>
                    <div className="font-mono text-[15px] text-oxblood">{MOCK.name}</div>
                    <div className="text-[12px] text-mulberry/60">Analyzed just now · {MOCK.files.toLocaleString()} files</div>
                  </div>
                </div>
                <Stat label="Stars" value={MOCK.stars} />
                <Stat label="Language" value={MOCK.language} />
                <Stat label="Modules" value="42" />
                <Stat label="Health" value="A+" accent />
              </motion.div>

              {/* Tree */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 }}
                className="col-span-12 md:col-span-4 acrylic p-5 rounded-2xl"
              >
                <PanelTitle>Folder Structure</PanelTitle>
                <div className="mt-3 font-mono text-[12.5px] space-y-1">
                  {MOCK.tree.map((n, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.25 + i * 0.04 }}
                      className="flex items-center gap-2 text-mulberry"
                      style={{ paddingLeft: n.depth * 14 }}
                    >
                      <span className="text-mulberry/40">{n.kind === "dir" ? "▸" : "·"}</span>
                      <span className={n.kind === "dir" ? "text-oxblood" : "text-mulberry/70"}>{n.name}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Graph */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="col-span-12 md:col-span-5 acrylic p-5 rounded-2xl"
              >
                <PanelTitle>Architecture</PanelTitle>
                <ArchGraph className="mt-2" />
              </motion.div>

              {/* Summary */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
                className="col-span-12 md:col-span-3 acrylic p-5 rounded-2xl"
              >
                <PanelTitle>Summary</PanelTitle>
                <p className="mt-3 text-[13px] leading-relaxed text-mulberry">
                  {MOCK.summary}
                </p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {["React", "SSR", "Webpack", "SWC", "Routing"].map((t) => (
                    <span key={t} className="text-[11px] px-2 py-0.5 rounded-full bg-oxblood/8 text-mulberry">{t}</span>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="flex flex-col">
      <span className="text-[11px] uppercase tracking-widest text-mulberry/50">{label}</span>
      <span className={`text-[15px] font-medium ${accent ? "text-burgundy" : "text-oxblood"}`}>{value}</span>
    </div>
  );
}

function PanelTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <h3 className="text-[11px] uppercase tracking-[0.18em] text-mulberry/70">{children}</h3>
      <span className="w-1.5 h-1.5 rounded-full bg-terracotta/70" />
    </div>
  );
}

function ArchGraph({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={`w-full aspect-[5/4] ${className ?? ""}`}>
      <defs>
        <radialGradient id="node" cx="50%" cy="35%">
          <stop offset="0" stopColor="#F0E6B1" />
          <stop offset="1" stopColor="#C7886B" />
        </radialGradient>
        <radialGradient id="nodeCore" cx="50%" cy="35%">
          <stop offset="0" stopColor="#E5C89B" />
          <stop offset="1" stopColor="#792E3C" />
        </radialGradient>
      </defs>
      {MOCK.edges.map(([a, b], i) => {
        const na = MOCK.nodes.find((n) => n.id === a)!;
        const nb = MOCK.nodes.find((n) => n.id === b)!;
        return (
          <motion.line
            key={i}
            x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
            stroke="#8E3E4D"
            strokeOpacity="0.35"
            strokeWidth="0.4"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.4, delay: 0.3 + i * 0.08 }}
          />
        );
      })}
      {MOCK.nodes.map((n, i) => (
        <motion.g
          key={n.id}
          initial={{ opacity: 0, scale: 0.6 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 + i * 0.08, duration: 0.6 }}
        >
          <circle
            cx={n.x}
            cy={n.y}
            r={n.r / 6}
            fill={n.id === "core" ? "url(#nodeCore)" : "url(#node)"}
            stroke="#5C1E2A"
            strokeOpacity="0.3"
            strokeWidth="0.3"
          />
          <text
            x={n.x}
            y={n.y + n.r / 6 + 4}
            textAnchor="middle"
            fontSize="2.6"
            fill="#5C1E2A"
            fontFamily="Inter, sans-serif"
          >
            {n.label}
          </text>
        </motion.g>
      ))}
    </svg>
  );
}

/* --------------------------- Section 2: Workflow --------------------------- */

const STEPS = [
  { title: "Paste Repository", body: "A single URL is enough. No installation, no auth, no setup." },
  { title: "Atlas scans the project", body: "Files, folders, manifests, and imports are read in seconds." },
  { title: "Architecture discovered", body: "Modules and their relationships surface as a live graph." },
  { title: "Dependencies mapped", body: "Every internal edge and external package accounted for." },
  { title: "Repository explained", body: "A calm narrative summary — written for humans, not crawlers." },
];

function Workflow() {
  return (
    <section id="features" className="relative py-40 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-[12px] uppercase tracking-[0.22em] text-mulberry/70">The journey</p>
          <h2 className="mt-4 font-serif text-[clamp(36px,5vw,64px)] leading-[1.05] text-oxblood max-w-2xl">
            From a URL to a mental model — <span className="italic text-burgundy">in seconds</span>.
          </h2>
        </motion.div>

        <div className="mt-20 relative">
          <div className="absolute left-6 top-4 bottom-4 w-px bg-gradient-to-b from-transparent via-oxblood/25 to-transparent" />
          <div className="space-y-14">
            {STEPS.map((s, i) => (
              <WorkflowStep key={i} index={i} title={s.title} body={s.body} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function WorkflowStep({ index, title, body }: { index: number; title: string; body: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="relative pl-16"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={inView ? { scale: 1 } : {}}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="absolute left-0 top-1 w-12 h-12 rounded-full acrylic-strong flex items-center justify-center font-serif text-[18px] text-burgundy"
      >
        {String(index + 1).padStart(2, "0")}
      </motion.div>
      <h3 className="font-serif text-[26px] text-oxblood leading-tight">{title}</h3>
      <p className="mt-2 text-mulberry/80 text-[15px] leading-relaxed max-w-xl">{body}</p>
    </motion.div>
  );
}

/* --------------------- Section 3: What Atlas Understands --------------------- */

type Capability = {
  key: string;
  title: string;
  blurb: string;
  Preview: React.FC;
};

const CAPS: Capability[] = [
  {
    key: "structure",
    title: "Repository Structure",
    blurb: "The whole tree, unfolded — from top-level packages to leaf files.",
    Preview: () => (
      <div className="font-mono text-[11.5px] space-y-1 text-mulberry">
        {MOCK.tree.slice(0, 8).map((n, i) => (
          <div key={i} style={{ paddingLeft: n.depth * 12 }} className="flex gap-2">
            <span className="text-mulberry/40">{n.kind === "dir" ? "▸" : "·"}</span>
            <span className={n.kind === "dir" ? "text-oxblood" : ""}>{n.name}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    key: "architecture",
    title: "Architecture",
    blurb: "The system's shape — modules, layers, and the edges between them.",
    Preview: () => <ArchGraph />,
  },
  {
    key: "deps",
    title: "Dependencies",
    blurb: "External packages and internal imports, weighted by usage.",
    Preview: () => (
      <div className="flex flex-wrap gap-1.5">
        {MOCK.deps.map((d, i) => (
          <span
            key={d}
            className="font-mono text-[11px] px-2 py-1 rounded-md bg-oxblood/6 text-mulberry"
            style={{ opacity: 1 - i * 0.07 }}
          >
            {d}
          </span>
        ))}
      </div>
    ),
  },
  {
    key: "stack",
    title: "Technology Stack",
    blurb: "The languages, frameworks, and tools that hold it together.",
    Preview: () => (
      <div className="grid grid-cols-3 gap-2">
        {["TypeScript", "React", "Node.js", "Webpack", "SWC", "PostCSS"].map((t) => (
          <div key={t} className="text-[12px] text-center py-2 rounded-lg bg-oxblood/5 text-mulberry border border-oxblood/10">{t}</div>
        ))}
      </div>
    ),
  },
  {
    key: "docs",
    title: "Documentation",
    blurb: "Every README, comment, and doc block — surfaced when you need it.",
    Preview: () => (
      <div className="space-y-1.5">
        <div className="h-2 rounded bg-oxblood/12 w-full" />
        <div className="h-2 rounded bg-oxblood/10 w-11/12" />
        <div className="h-2 rounded bg-oxblood/8 w-9/12" />
        <div className="h-2 rounded bg-oxblood/12 w-10/12" />
        <div className="h-2 rounded bg-oxblood/10 w-8/12" />
      </div>
    ),
  },
  {
    key: "search",
    title: "Search",
    blurb: "Ask in plain language. Get the file, function, and line.",
    Preview: () => (
      <div className="acrylic-strong rounded-lg p-2.5 flex items-center gap-2">
        <span className="text-mulberry/50 text-[13px]">⌘K</span>
        <span className="font-mono text-[12px] text-mulberry">where is the request handler?</span>
      </div>
    ),
  },
  {
    key: "insights",
    title: "Insights",
    blurb: "Complexity, coupling, hot paths — the things worth reading first.",
    Preview: () => (
      <div className="space-y-2">
        {[["Complexity", 62], ["Coupling", 34], ["Coverage", 81]].map(([l, v]) => (
          <div key={l as string}>
            <div className="flex justify-between text-[11px] text-mulberry/70 mb-0.5">
              <span>{l}</span><span>{v}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-oxblood/10 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-terracotta to-burgundy"
                initial={{ width: 0 }}
                animate={{ width: `${v}%` }}
                transition={{ duration: 1 }}
              />
            </div>
          </div>
        ))}
      </div>
    ),
  },
];

function Capabilities() {
  const [open, setOpen] = useState<string | null>(null);

  return (
    <section className="relative py-40 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="max-w-2xl"
        >
          <p className="text-[12px] uppercase tracking-[0.22em] text-mulberry/70">What Atlas understands</p>
          <h2 className="mt-4 font-serif text-[clamp(36px,5vw,64px)] leading-[1.05] text-oxblood">
            Seven views of the same repository.
          </h2>
        </motion.div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-[minmax(180px,auto)]">
          {CAPS.map((c, i) => {
            const isOpen = open === c.key;
            return (
              <motion.button
                key={c.key}
                layout
                onClick={() => setOpen(isOpen ? null : c.key)}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.6, delay: i * 0.05, layout: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } }}
                whileHover={{ y: -3 }}
                className={`acrylic p-6 rounded-2xl text-left group ${isOpen ? "md:col-span-2 lg:col-span-2 row-span-2" : ""}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-[11px] uppercase tracking-[0.18em] text-mulberry/60">{String(i + 1).padStart(2, "0")}</div>
                    <h3 className="mt-2 font-serif text-[24px] text-oxblood leading-tight">{c.title}</h3>
                  </div>
                  <motion.span
                    animate={{ rotate: isOpen ? 45 : 0 }}
                    className="text-mulberry/50 text-2xl leading-none"
                  >+</motion.span>
                </div>
                <p className="mt-3 text-[13.5px] text-mulberry/80 leading-relaxed">{c.blurb}</p>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ opacity: 0, height: 0, marginTop: 0 }}
                      animate={{ opacity: 1, height: "auto", marginTop: 20 }}
                      exit={{ opacity: 0, height: 0, marginTop: 0 }}
                      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                      className="overflow-hidden"
                    >
                      <div className="pt-4 border-t border-oxblood/10">
                        <c.Preview />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* -------------------- Section 4: Live Product Preview -------------------- */

function LivePreview() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [40, -40]);
  const rotate = useTransform(scrollYProgress, [0, 1], [1.2, -1.2]);

  return (
    <section id="demo" ref={ref} className="relative py-40 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-2xl mx-auto"
        >
          <p className="text-[12px] uppercase tracking-[0.22em] text-mulberry/70">The workspace</p>
          <h2 className="mt-4 font-serif text-[clamp(36px,5vw,64px)] leading-[1.05] text-oxblood">
            One quiet surface for the whole repository.
          </h2>
        </motion.div>

        <motion.div style={{ y, rotate }} className="mt-20">
          <div className="acrylic-strong rounded-3xl overflow-hidden p-3">
            <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-[#fbf3dc] to-[#f0d9b6]">
              {/* Titlebar */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-oxblood/10">
                <div className="flex gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-oxblood/25" />
                  <span className="w-2.5 h-2.5 rounded-full bg-oxblood/25" />
                  <span className="w-2.5 h-2.5 rounded-full bg-oxblood/25" />
                </div>
                <div className="ml-4 flex items-center gap-2 text-[12px] text-mulberry/70 font-mono">
                  <AtlasMark size={14} /> atlas · {MOCK.name}
                </div>
                <div className="ml-auto acrylic px-3 py-1 rounded-md text-[11px] text-mulberry/70 flex items-center gap-2 font-mono">
                  <span className="text-mulberry/50">⌘K</span> where is the request handler?
                </div>
              </div>

              {/* Body: 3 panes */}
              <div className="grid grid-cols-12 min-h-[520px]">
                {/* Explorer */}
                <div className="col-span-3 border-r border-oxblood/10 p-4 bg-oxblood/[0.02]">
                  <div className="text-[10px] uppercase tracking-[0.18em] text-mulberry/60 mb-3">Explorer</div>
                  <div className="font-mono text-[12px] space-y-1">
                    {MOCK.tree.map((n, i) => (
                      <div
                        key={i}
                        className={`flex items-center gap-2 py-0.5 rounded ${i === 3 ? "bg-burgundy/10 text-oxblood" : "text-mulberry/85"}`}
                        style={{ paddingLeft: n.depth * 12 + 6 }}
                      >
                        <span className="text-mulberry/40">{n.kind === "dir" ? "▸" : "·"}</span>
                        {n.name}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Center: graph + summary */}
                <div className="col-span-6 p-6 flex flex-col gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-terracotta to-burgundy flex items-center justify-center text-parchment font-serif">n</div>
                    <div>
                      <div className="font-mono text-[13px] text-oxblood">{MOCK.name}</div>
                      <div className="text-[11px] text-mulberry/60">Architecture · 6 modules · 12 edges</div>
                    </div>
                  </div>
                  <div className="acrylic rounded-xl p-4 flex-1">
                    <ArchGraph />
                  </div>
                  <div className="acrylic rounded-xl p-4">
                    <div className="text-[10px] uppercase tracking-[0.18em] text-mulberry/60">Summary</div>
                    <p className="mt-1.5 text-[12.5px] text-mulberry leading-relaxed">
                      {MOCK.summary}
                    </p>
                  </div>
                </div>

                {/* Documentation */}
                <div className="col-span-3 border-l border-oxblood/10 p-4 bg-oxblood/[0.02]">
                  <div className="text-[10px] uppercase tracking-[0.18em] text-mulberry/60 mb-3">server/next-server.ts</div>
                  <div className="space-y-2 font-mono text-[11.5px] text-mulberry">
                    <div className="text-mulberry/50">// Entry for the Next.js server.</div>
                    <div><span className="text-burgundy">export class</span> NextServer &#123;</div>
                    <div className="pl-3"><span className="text-burgundy">async</span> handleRequest(req) &#123;</div>
                    <div className="pl-6 text-mulberry/70">return this.router.match(req)</div>
                    <div className="pl-3">&#125;</div>
                    <div>&#125;</div>
                    <div className="mt-4 text-[10px] uppercase tracking-[0.18em] text-mulberry/60">Uses</div>
                    <div className="flex flex-wrap gap-1">
                      {["router", "cache", "logger"].map((t) => (
                        <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-oxblood/8">{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* ---------------------------- Section 5: CTA ---------------------------- */

function FinalCTA() {
  return (
    <section className="relative py-40 px-6">
      <div className="max-w-3xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.9 }}
          className="font-serif text-[clamp(40px,6vw,80px)] leading-[1.02] text-oxblood"
        >
          Ready to understand your <span className="italic text-burgundy">next repository</span>?
        </motion.h2>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, delay: 0.15 }}
          className="mt-12 flex flex-wrap justify-center gap-3"
        >
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="px-7 py-3.5 rounded-xl bg-oxblood text-parchment text-[14px] font-medium flex items-center gap-2"
            style={{ boxShadow: "inset 0 1px 0 rgba(240,230,177,0.2), 0 12px 30px -12px rgba(92,30,42,0.6)" }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.09.68-.22.68-.49v-1.7c-2.78.62-3.37-1.35-3.37-1.35-.45-1.17-1.11-1.48-1.11-1.48-.91-.63.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.27 2.75 1.05a9.4 9.4 0 0 1 5 0c1.91-1.32 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9v2.82c0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2z"/></svg>
            Continue with GitHub
          </motion.button>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
            <Link
              to="/explore"
              className="acrylic-strong inline-block px-7 py-3.5 rounded-xl text-oxblood text-[14px] font-medium"
            >
              Explore Demo →
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

/* --------------------------------- Root --------------------------------- */

function AtlasLanding() {
  useEffect(() => {
    document.documentElement.style.scrollBehavior = "smooth";
  }, []);
  return (
    <div className="relative min-h-screen">
      <LivingBackground />
      <Nav />
      <main>
        <Hero />
        <Workflow />
        <Capabilities />
        <LivePreview />
        <FinalCTA />
      </main>
      <div className="py-10 text-center text-[11px] tracking-[0.2em] uppercase text-mulberry/50">
        <AtlasMark size={16} />
        <span className="ml-2 align-middle">Atlas · A workspace for reading code</span>
      </div>
    </div>
  );
}
