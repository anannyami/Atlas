import { useState } from "react";
import { motion } from "motion/react";
import { useNavigate } from "@tanstack/react-router";
import { Upload, Sparkles, ArrowUpRight } from "lucide-react";
import { recentlyAnalyzed } from "@/lib/mock-repositories";

export function AnalyzeRepositoryPanel() {
  const [url, setUrl] = useState("");
  const [focused, setFocused] = useState(false);
  const navigate = useNavigate();

  const submit = () => {
    navigate({ to: "/repository/$id", params: { id: "custom" } });
  };

  return (
    <section className="relative">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="acrylic-strong p-8 md:p-10 relative overflow-hidden"
      >
        <div
          className="absolute -top-24 -right-24 w-72 h-72 rounded-full opacity-50 pointer-events-none"
          style={{ background: "radial-gradient(circle, #C7886B, transparent 65%)", filter: "blur(40px)" }}
        />
        <div className="relative flex flex-col items-center text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-oxblood/5 border border-oxblood/10 text-[11px] font-mono tracking-wider uppercase text-mulberry/70">
            <Sparkles size={12} /> Bring your own
          </div>
          <h2 className="font-serif text-4xl md:text-5xl text-oxblood mt-4 leading-[1.05] tracking-tight">
            Analyze your own repository.
          </h2>
          <p className="mt-3 text-[14px] text-mulberry/75 max-w-md">
            Paste a public GitHub URL. Atlas will map the architecture, dependencies, and structure before you read a single file.
          </p>

          <div className="w-full mt-7">
            <motion.div
              animate={{
                boxShadow: focused
                  ? "0 0 0 3px rgba(120,46,60,0.15), 0 20px 40px -20px rgba(92,30,42,0.4)"
                  : "0 8px 20px -12px rgba(92,30,42,0.25)",
              }}
              className="flex items-center gap-2 p-2 rounded-2xl bg-[rgba(255,248,228,0.9)] border border-oxblood/10"
            >
              <div className="pl-3 pr-1 font-mono text-[13px] text-mulberry/50 select-none hidden sm:block">https://</div>
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                placeholder="github.com/owner/repository"
                className="flex-1 bg-transparent outline-none text-[14px] font-mono text-oxblood placeholder:text-mulberry/40 py-2.5 min-w-0"
              />
              <button
                onClick={submit}
                className="hidden sm:inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-oxblood hover:bg-burgundy text-parchment text-[13px] font-medium transition"
                style={{ boxShadow: "inset 0 1px 0 rgba(240,230,177,0.2)" }}
              >
                Analyze Repository <ArrowUpRight size={14} />
              </button>
            </motion.div>
            <div className="mt-3 flex items-center justify-center gap-3 text-[12px] text-mulberry/60">
              <button className="sm:hidden inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-oxblood text-parchment">
                Analyze <ArrowUpRight size={14} />
              </button>
              <span className="hidden sm:inline">or</span>
              <button className="inline-flex items-center gap-1.5 text-mulberry/80 hover:text-oxblood transition">
                <Upload size={13} /> Upload ZIP
              </button>
            </div>
          </div>

          <div className="w-full mt-9">
            <div className="text-[10.5px] font-mono uppercase tracking-wider text-mulberry/50 mb-2 text-left">
              Recently analyzed
            </div>
            <ul className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {recentlyAnalyzed.map((r) => (
                <li key={r.id}>
                  <button
                    onClick={() => navigate({ to: "/repository/$id", params: { id: r.id } })}
                    className="w-full text-left px-3 py-2.5 rounded-xl bg-[rgba(255,248,228,0.6)] border border-oxblood/10 hover:border-oxblood/25 hover:bg-[rgba(255,248,228,0.9)] transition group"
                  >
                    <div className="font-mono text-[12.5px] text-oxblood truncate">{r.name}</div>
                    <div className="text-[11px] text-mulberry/60">{r.when}</div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
