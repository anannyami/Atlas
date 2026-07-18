import { useState } from "react";
import { motion } from "motion/react";
import { Search, Copy } from "lucide-react";
import type { Repository } from "@/lib/mock-repositories";

const sections = [
  { id: "intro", title: "Introduction" },
  { id: "install", title: "Installation" },
  { id: "arch", title: "Architecture" },
  { id: "usage", title: "Usage" },
  { id: "contrib", title: "Contributing" },
];

export function DocumentationPanel({ repo }: { repo: Repository }) {
  const [active, setActive] = useState("intro");
  const [q, setQ] = useState("");

  return (
    <div className="max-w-5xl mx-auto px-10 py-10 grid grid-cols-[1fr_200px] gap-10">
      <article className="min-w-0">
        <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Documentation</div>
        <h1 id="intro" className="font-serif text-[40px] text-oxblood leading-tight mt-1">
          {repo.owner}/{repo.name}
        </h1>
        <div className="prose-atlas mt-6 space-y-6 text-[14.5px] text-oxblood/85 leading-[1.75]">
          <p className="font-serif text-[19px] italic text-mulberry/80 leading-[1.55]">
            {repo.description}
          </p>

          <h2 id="install" className="font-serif text-[26px] text-oxblood pt-6">Installation</h2>
          <p>Clone the repository and install dependencies with your package manager of choice.</p>
          <div className="rounded-lg bg-oxblood/[0.06] border border-oxblood/10 p-3 pr-2 flex items-center justify-between">
            <code className="font-mono text-[12.5px] text-oxblood">git clone github.com/{repo.owner}/{repo.name}.git</code>
            <button className="p-1.5 rounded hover:bg-oxblood/10 text-mulberry/60"><Copy size={13} /></button>
          </div>

          <h2 id="arch" className="font-serif text-[26px] text-oxblood pt-6">Architecture</h2>
          <p>
            {repo.name} is organised as a <b>{repo.architecture.split("·")[0].trim()}</b>. The root
            contains configuration and manifests; every runtime concern lives under <code className="font-mono text-[12.5px] px-1 py-0.5 bg-oxblood/[0.06] rounded">src/</code>.
          </p>
          <p>
            Read the folders in this order: components, hooks, services, pages. Each layer builds on the one above it.
          </p>

          <h2 id="usage" className="font-serif text-[26px] text-oxblood pt-6">Usage</h2>
          <p>
            The main entry point boots providers, mounts the router, and hands control to page components. State is co-located
            with the screens that need it; anything shared is lifted into a hook.
          </p>

          <h2 id="contrib" className="font-serif text-[26px] text-oxblood pt-6">Contributing</h2>
          <p>
            Read <code className="font-mono text-[12.5px] px-1 py-0.5 bg-oxblood/[0.06] rounded">CONTRIBUTING.md</code>, run the test suite locally, and open a draft pull request early. The maintainers prefer small, focused changes.
          </p>
        </div>
      </article>

      <aside className="sticky top-6 self-start">
        <div className="acrylic p-3 mb-3 flex items-center gap-2">
          <Search size={13} className="text-mulberry/55 ml-1" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search docs…"
            className="flex-1 bg-transparent outline-none text-[12.5px] text-oxblood placeholder:text-mulberry/45 py-1"
          />
        </div>
        <div className="text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/55 mb-2 px-2">On this page</div>
        <nav className="space-y-0.5">
          {sections
            .filter((s) => !q || s.title.toLowerCase().includes(q.toLowerCase()))
            .map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                onClick={() => setActive(s.id)}
                className={`block px-2 py-1.5 rounded-md text-[13px] transition relative ${
                  active === s.id ? "text-oxblood" : "text-mulberry/65 hover:text-oxblood"
                }`}
              >
                {active === s.id && (
                  <motion.span layoutId="doc-active" className="absolute left-0 top-2 bottom-2 w-[2px] bg-oxblood rounded-r" />
                )}
                <span className="ml-2">{s.title}</span>
              </a>
            ))}
        </nav>
      </aside>
    </div>
  );
}
