import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { motion } from "motion/react";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { RepositoryGrid } from "@/components/workspace/RepositoryGrid";
import { AnalyzeRepositoryPanel } from "@/components/workspace/AnalyzeRepositoryPanel";
import { RecentRepositoryCard } from "@/components/workspace/RecentRepositoryCard";
import { RecentActivity } from "@/components/workspace/RecentActivity";
import { RepositorySearch } from "@/components/workspace/RepositorySearch";
import { featuredRepositories, continueRepos, recentActivity } from "@/lib/mock-repositories";
import { Compass } from "lucide-react";

export const Route = createFileRoute("/explore")({
  head: () => ({
    meta: [
      { title: "Explore — Atlas" },
      {
        name: "description",
        content:
          "Choose a repository to explore in Atlas. Curated codebases or analyze your own GitHub project.",
      },
      { property: "og:title", content: "Atlas — Explore" },
      { property: "og:description", content: "A calm workspace to explore any codebase." },
    ],
  }),
  component: ExplorePage,
});

function LivingBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 atlas-stage atlas-noise">
      <motion.div
        className="atlas-blob"
        style={{
          width: 900,
          height: 900,
          top: "-25%",
          left: "-15%",
          background: "radial-gradient(circle, #F0E6B1, transparent 60%)",
        }}
        animate={{ x: [0, 60, -20, 0], y: [0, 40, -30, 0] }}
        transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="atlas-blob"
        style={{
          width: 800,
          height: 800,
          top: "20%",
          right: "-15%",
          background: "radial-gradient(circle, #C7886B, transparent 65%)",
          opacity: 0.5,
        }}
        animate={{ x: [0, -50, 30, 0], y: [0, 60, 20, 0] }}
        transition={{ duration: 34, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="atlas-blob"
        style={{
          width: 900,
          height: 900,
          bottom: "-30%",
          left: "30%",
          background: "radial-gradient(circle, #8E3E4D, transparent 60%)",
          opacity: 0.35,
        }}
        animate={{ x: [0, 40, -30, 0], y: [0, -30, 20, 0] }}
        transition={{ duration: 38, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

function ExplorePage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return featuredRepositories.filter((r) => {
      const matchesFilter = filter === "All" || r.language === filter || r.difficulty === filter;
      if (!matchesFilter) return false;
      if (!q) return true;
      const hay = [r.name, r.owner, r.description, r.framework, r.language, ...r.technologies]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
  }, [query, filter]);

  const hasContinue = continueRepos.length > 0;

  return (
    <div className="relative min-h-screen">
      <LivingBackground />
      <WorkspaceHeader />

      <main className="pt-28 pb-32">
        {/* Heading */}
        <section className="max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-oxblood/5 border border-oxblood/10 text-[11px] font-mono tracking-wider uppercase text-mulberry/70">
              <Compass size={12} /> Workspace
            </div>
            <h1 className="mt-4 font-serif text-5xl md:text-6xl leading-[1.02] tracking-tight text-oxblood max-w-3xl">
              Choose a repository to explore.
            </h1>
            <p className="mt-4 text-[15px] text-mulberry/75 max-w-xl">
              Start with one of our curated repositories or analyze your own GitHub project. Atlas
              will lay out its architecture so you can read with intent.
            </p>
          </motion.div>
        </section>

        <div className="divider-fade max-w-6xl mx-auto my-10 mx-6" />

        {/* Featured */}
        <section className="max-w-6xl mx-auto px-6">
          <div className="flex items-end justify-between gap-4 mb-5">
            <div>
              <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/60">
                Section 01
              </div>
              <h2 className="font-serif text-3xl text-oxblood mt-1">Featured repositories</h2>
            </div>
            <div className="text-[12px] text-mulberry/60 hidden md:block">
              {filtered.length} of {featuredRepositories.length}
            </div>
          </div>

          <div className="mb-6">
            <RepositorySearch
              value={query}
              onChange={setQuery}
              activeFilter={filter}
              onFilter={setFilter}
            />
          </div>

          {filtered.length > 0 ? (
            <RepositoryGrid repositories={filtered} />
          ) : (
            <EmptyState
              title="No repositories match that search"
              body="Try a broader term, clear the filter, or paste a GitHub URL below to analyze your own."
            />
          )}
        </section>

        {/* Analyze */}
        <section className="max-w-4xl mx-auto px-6 mt-24">
          <AnalyzeRepositoryPanel />
        </section>

        {/* Continue */}
        <section className="max-w-6xl mx-auto px-6 mt-24">
          <div className="mb-5">
            <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/60">
              Section 03
            </div>
            <h2 className="font-serif text-3xl text-oxblood mt-1">Continue where you left off</h2>
          </div>
          {hasContinue ? (
            <div className="flex gap-4 overflow-x-auto pb-3 -mx-6 px-6 snap-x">
              {continueRepos.map((r, i) => (
                <div key={r.id} className="snap-start">
                  <RecentRepositoryCard repo={r} index={i} />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Nothing to resume yet"
              body="Open a repository and Atlas will remember where you paused."
            />
          )}
        </section>

        {/* Activity */}
        <section className="max-w-4xl mx-auto px-6 mt-24">
          <div className="mb-5">
            <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/60">
              Section 04
            </div>
            <h2 className="font-serif text-3xl text-oxblood mt-1">Recent activity</h2>
          </div>
          <div className="acrylic p-6">
            <RecentActivity items={recentActivity} />
          </div>
        </section>
      </main>
    </div>
  );
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="acrylic p-10 flex flex-col items-center text-center">
      <svg width="88" height="88" viewBox="0 0 88 88" fill="none">
        <defs>
          <linearGradient id="empty-g" x1="0" y1="0" x2="88" y2="88">
            <stop offset="0" stopColor="#C7886B" />
            <stop offset="1" stopColor="#792E3C" />
          </linearGradient>
        </defs>
        <circle
          cx="44"
          cy="44"
          r="34"
          stroke="url(#empty-g)"
          strokeWidth="1.5"
          fill="none"
          opacity="0.6"
        />
        <path
          d="M44 20 C 56 34, 56 54, 44 68 M44 20 C 32 34, 32 54, 44 68 M14 44 H74"
          stroke="url(#empty-g)"
          strokeWidth="1.2"
          fill="none"
          opacity="0.7"
        />
        <circle cx="44" cy="44" r="4" fill="#792E3C" />
      </svg>
      <h3 className="font-serif text-2xl text-oxblood mt-4">{title}</h3>
      <p className="text-[13.5px] text-mulberry/70 mt-2 max-w-sm">{body}</p>
    </div>
  );
}
