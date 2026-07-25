import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  AlertCircle,
  ArrowRight,
  Boxes,
  Check,
  Code2,
  Eye,
  FileText,
  Gauge,
  GitBranch,
  Layers,
  Loader2,
  Lock,
  LogOut,
  RefreshCw,
  Shield,
  Sparkles,
  UserRoundCog,
  Users,
  WifiOff,
} from "lucide-react";
import { AuthService, GitHubService } from "@/services";
import type { AuthProgress, AuthStage, GitHubProfile, RepositorySummary } from "@/services";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useAuth, initials } from "@/lib/auth";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Connect GitHub — Atlas" },
      {
        name: "description",
        content:
          "Sign in with GitHub to explore, analyze, and understand any repository inside the Atlas workspace.",
      },
      { property: "og:title", content: "Connect GitHub — Atlas" },
      {
        property: "og:description",
        content: "Bring your repositories into a workspace built for reading unfamiliar code.",
      },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: AuthPage,
});

type UiStatus = "idle" | "loading" | "success" | "error";
type ErrorKind = "network" | "unauthorized" | "expired" | "generic";

// ---------------------------------------------------------------------------
// Capabilities & permissions (editorial content)
// ---------------------------------------------------------------------------
const capabilities = [
  {
    icon: Layers,
    title: "Architecture visualization",
    body: "See how folders, packages, and services connect.",
  },
  {
    icon: Boxes,
    title: "Dependency analysis",
    body: "Trace every dependency, direct and transitive.",
  },
  {
    icon: FileText,
    title: "Documentation explorer",
    body: "Browse READMEs and docs with search and syntax highlighting.",
  },
  {
    icon: Code2,
    title: "Technology detection",
    body: "Every framework and tool, categorized and explained.",
  },
  {
    icon: Gauge,
    title: "Repository health",
    body: "Maturity, docs, and maintainability scores at a glance.",
  },
  {
    icon: Sparkles,
    title: "Complexity analysis",
    body: "Hot spots and refactoring opportunities per file.",
  },
  {
    icon: Shield,
    title: "Security insights",
    body: "Known advisories and configuration risks surfaced.",
  },
  {
    icon: UserRoundCog,
    title: "AI repository explanations",
    body: "Ask why a piece of code exists — in plain English.",
  },
];

const permissions = [
  "Repository metadata",
  "Repository contents",
  "Branches",
  "Pull Requests",
  "Issues",
  "Commits",
  "Languages",
  "Contributors",
  "README",
  "Releases",
];

const supportedRepoTypes = ["Public", "Private", "Organizations", "Forks", "Archived (read-only)"];

const STAGE_ORDER: AuthStage[] = [
  "connecting",
  "redirecting",
  "authorizing",
  "fetching_profile",
  "fetching_repositories",
  "completed",
];

const STAGE_LABEL: Record<AuthStage, string> = {
  connecting: "Connecting",
  redirecting: "Redirecting",
  authorizing: "Authorizing",
  fetching_profile: "Fetching profile",
  fetching_repositories: "Fetching repositories",
  completed: "Completed",
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
function AuthPage() {
  const navigate = useNavigate();
  const { user, hydrated, disconnect } = useAuth();
  const [status, setStatus] = useState<UiStatus>("idle");
  const [progress, setProgress] = useState<AuthProgress>({
    stage: "connecting",
    message: "",
    progress: 0,
  });
  const [error, setError] = useState<{ kind: ErrorKind; message: string } | null>(null);
  const [simulate, setSimulate] = useState<"network" | "unauthorized" | "expired" | undefined>();
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  async function handleSignIn(nextSimulate?: "network" | "unauthorized" | "expired") {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus("loading");
    setError(null);
    setProgress({ stage: "connecting", message: "Reaching GitHub", progress: 0 });
    try {
      await AuthService.signInWithGitHub({
        signal: controller.signal,
        simulate: nextSimulate,
        onProgress: setProgress,
      });
      setStatus("success");
      setTimeout(() => navigate({ to: "/explore" }), 900);
    } catch (e) {
      const anyE = e as { code?: string; message?: string };
      if (anyE.code === "aborted") return;
      const kind: ErrorKind =
        anyE.code === "network_error"
          ? "network"
          : anyE.code === "unauthorized"
            ? "unauthorized"
            : anyE.code === "session_expired"
              ? "expired"
              : "generic";
      setError({ kind, message: anyE.message ?? "Something went wrong." });
      setStatus("error");
    }
  }

  return (
    <div
      className="min-h-screen w-full relative overflow-hidden"
      style={{
        background:
          "radial-gradient(1200px 700px at 15% -5%, rgba(199,136,107,0.18), transparent 60%), radial-gradient(900px 500px at 90% 110%, rgba(120,46,60,0.14), transparent 55%), var(--color-parchment, #F6EFDD)",
      }}
    >
      {/* Grain */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.35] mix-blend-multiply"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 30%, rgba(120,46,60,0.09), transparent 40%), radial-gradient(circle at 80% 70%, rgba(199,136,107,0.11), transparent 45%)",
        }}
      />

      <div className="relative mx-auto max-w-[1240px] px-6 lg:px-10 pt-6 pb-16">
        <div className="flex items-center justify-between">
          <Link
            to="/"
            className="text-[13px] text-mulberry/70 hover:text-oxblood transition inline-flex items-center gap-1.5"
          >
            <span className="translate-y-[-1px]">←</span> Back to Atlas
          </Link>
          <div className="hidden sm:flex items-center gap-1.5 text-[11.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">
            <span className="h-1.5 w-1.5 rounded-full bg-[#5C7C4A]" />
            OAuth is read-only
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(420px,520px)] gap-10 lg:gap-14 items-start">
          <MarketingColumn />
          <div className="lg:sticky lg:top-8">
            <AnimatePresence mode="wait">
              {hydrated && user && status !== "loading" && status !== "success" && !error ? (
                <ProfilePanel
                  key="profile"
                  profile={user}
                  onDisconnect={disconnect}
                  onSwitch={() => handleSignIn()}
                />
              ) : (
                <motion.div
                  key="auth-card"
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.4, ease: [0.22, 0.9, 0.32, 1] }}
                >
                  <AuthCard
                    status={status}
                    progress={progress}
                    error={error}
                    simulate={simulate}
                    setSimulate={setSimulate}
                    onSignIn={() => handleSignIn(simulate)}
                    onRetry={() => handleSignIn(simulate)}
                    onCancel={() => {
                      abortRef.current?.abort();
                      setStatus("idle");
                    }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Marketing / capabilities column
// ---------------------------------------------------------------------------
function MarketingColumn() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 0.9, 0.32, 1] }}
      className="max-w-xl"
    >
      <div className="text-[10.5px] font-mono uppercase tracking-[0.24em] text-mulberry/55">
        Atlas · Repository Intelligence
      </div>
      <h1 className="mt-3 font-serif text-[54px] leading-[1.02] text-oxblood tracking-tight">
        Read any codebase
        <br />
        the way its <em className="italic text-burgundy">authors</em> would.
      </h1>
      <p className="mt-5 text-[15px] leading-relaxed text-mulberry/80 max-w-lg">
        Sign in with GitHub to open your repositories inside a workspace built for architecture,
        dependencies, documentation, and health — all in one editorial view.
      </p>

      <div className="mt-9 grid grid-cols-1 sm:grid-cols-2 gap-3">
        {capabilities.map((c, i) => (
          <motion.div
            key={c.title}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.05 + i * 0.03 }}
            className="rounded-2xl p-4 border border-oxblood/10 bg-parchment/40 backdrop-blur-[2px]"
          >
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-xl bg-oxblood/[0.06] border border-oxblood/10 flex items-center justify-center text-oxblood">
                <c.icon size={15} />
              </div>
              <div className="font-serif text-[16px] text-oxblood leading-tight">{c.title}</div>
            </div>
            <p className="mt-2 text-[12.5px] text-mulberry/75 leading-relaxed">{c.body}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap gap-3 text-[12px] text-mulberry/70">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-oxblood/[0.05] border border-oxblood/10">
          <Lock size={12} /> Read-only OAuth
        </span>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-oxblood/[0.05] border border-oxblood/10">
          <Shield size={12} /> No writes, no destructive actions
        </span>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-oxblood/[0.05] border border-oxblood/10">
          <Eye size={12} /> Session persists across visits
        </span>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Auth card
// ---------------------------------------------------------------------------
function AuthCard({
  status,
  progress,
  error,
  simulate,
  setSimulate,
  onSignIn,
  onRetry,
  onCancel,
}: {
  status: UiStatus;
  progress: AuthProgress;
  error: { kind: ErrorKind; message: string } | null;
  simulate: "network" | "unauthorized" | "expired" | undefined;
  setSimulate: (v: "network" | "unauthorized" | "expired" | undefined) => void;
  onSignIn: () => void;
  onRetry: () => void;
  onCancel: () => void;
}) {
  return (
    <div
      className="acrylic-strong rounded-3xl p-7 relative overflow-hidden"
      style={{
        boxShadow: "0 30px 60px -30px rgba(92,30,42,0.35), inset 0 1px 0 rgba(255,246,224,0.5)",
      }}
    >
      <CardHeader />

      <AnimatePresence mode="wait">
        {status === "loading" ? (
          <LoadingBlock key="loading" progress={progress} onCancel={onCancel} />
        ) : status === "success" ? (
          <SuccessBlock key="success" />
        ) : status === "error" && error ? (
          <ErrorBlock key="err" kind={error.kind} message={error.message} onRetry={onRetry} />
        ) : (
          <IdleBlock key="idle" onSignIn={onSignIn} simulate={simulate} setSimulate={setSimulate} />
        )}
      </AnimatePresence>
    </div>
  );
}

function CardHeader() {
  return (
    <div className="flex items-center gap-3.5 mb-6">
      <div
        className="h-11 w-11 rounded-2xl flex items-center justify-center text-parchment relative"
        style={{ background: "linear-gradient(135deg, #C7886B 0%, #5C1E2A 100%)" }}
      >
        <GitHubMark size={22} />
        <motion.span
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15, type: "spring", stiffness: 260, damping: 18 }}
          className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-parchment border border-oxblood/15 flex items-center justify-center text-oxblood"
        >
          <Lock size={10} />
        </motion.span>
      </div>
      <div>
        <div className="font-serif text-[22px] text-oxblood leading-none tracking-tight">
          Connect GitHub
        </div>
        <div className="text-[12px] text-mulberry/70 mt-1.5">
          Read-only · OAuth 2.0 · Revoke anytime
        </div>
      </div>
    </div>
  );
}

function IdleBlock({
  onSignIn,
  simulate,
  setSimulate,
}: {
  onSignIn: () => void;
  simulate: "network" | "unauthorized" | "expired" | undefined;
  setSimulate: (v: "network" | "unauthorized" | "expired" | undefined) => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.3 }}
    >
      <div>
        <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-mulberry/55 mb-2.5">
          Permissions requested
        </div>
        <ul className="grid grid-cols-2 gap-x-3 gap-y-1.5">
          {permissions.map((p) => (
            <li key={p} className="flex items-center gap-2 text-[12.5px] text-oxblood">
              <Check size={13} className="text-[#3E5C30] shrink-0" />
              <span>{p}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-6">
        <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-mulberry/55 mb-2.5">
          Supported repositories
        </div>
        <div className="flex flex-wrap gap-1.5">
          {supportedRepoTypes.map((t) => (
            <span
              key={t}
              className="text-[11.5px] px-2 py-0.5 rounded-full bg-oxblood/[0.05] border border-oxblood/10 text-mulberry/85"
            >
              {t}
            </span>
          ))}
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.005 }}
        whileTap={{ scale: 0.985 }}
        onClick={onSignIn}
        className="mt-6 w-full inline-flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-xl bg-oxblood text-parchment text-[14px] font-medium hover:bg-burgundy transition"
        style={{
          boxShadow: "inset 0 1px 0 rgba(240,230,177,0.2), 0 14px 34px -14px rgba(92,30,42,0.6)",
        }}
      >
        <GitHubMark size={16} /> Sign in with GitHub
      </motion.button>

      <div className="mt-4 flex items-center justify-between text-[11px] text-mulberry/60">
        <span className="inline-flex items-center gap-1.5">
          <Lock size={11} /> No writes. No repository modifications.
        </span>
        <details className="group">
          <summary className="cursor-pointer list-none hover:text-oxblood transition">
            Simulate state
          </summary>
          <div className="absolute right-6 mt-2 z-10 acrylic p-2 rounded-xl flex flex-col gap-1 text-[11.5px]">
            {(["network", "unauthorized", "expired"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setSimulate(simulate === s ? undefined : s)}
                className={`text-left px-2 py-1 rounded-md hover:bg-oxblood/[0.06] ${
                  simulate === s ? "text-oxblood font-medium" : "text-mulberry/80"
                }`}
              >
                {simulate === s ? "✓ " : ""}
                {s === "network"
                  ? "Network error"
                  : s === "unauthorized"
                    ? "Unauthorized"
                    : "Session expired"}
              </button>
            ))}
          </div>
        </details>
      </div>
    </motion.div>
  );
}

function LoadingBlock({ progress, onCancel }: { progress: AuthProgress; onCancel: () => void }) {
  const pct = Math.max(0.03, progress.progress);
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.25 }}
    >
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-full bg-oxblood/[0.06] flex items-center justify-center text-oxblood">
          <Loader2 size={18} className="animate-spin" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[14px] text-oxblood font-medium truncate">{progress.message}</div>
          <div className="text-[11.5px] text-mulberry/65">
            {STAGE_LABEL[progress.stage]} · {Math.round(pct * 100)}%
          </div>
        </div>
      </div>

      <div className="mt-4 h-1.5 rounded-full bg-oxblood/[0.07] overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: "linear-gradient(90deg, #C7886B, #792E3C)" }}
          animate={{ width: `${pct * 100}%` }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        />
      </div>

      <ol className="mt-5 space-y-2">
        {STAGE_ORDER.map((stage) => {
          const idx = STAGE_ORDER.indexOf(stage);
          const cur = STAGE_ORDER.indexOf(progress.stage);
          const state = idx < cur ? "done" : idx === cur ? "active" : "pending";
          return (
            <li key={stage} className="flex items-center gap-2.5 text-[12.5px]">
              <span
                className={`h-4 w-4 rounded-full flex items-center justify-center shrink-0 ${
                  state === "done"
                    ? "bg-[#5C7C4A] text-parchment"
                    : state === "active"
                      ? "bg-oxblood text-parchment"
                      : "bg-oxblood/[0.08] text-mulberry/50"
                }`}
              >
                {state === "done" ? (
                  <Check size={10} />
                ) : state === "active" ? (
                  <Loader2 size={9} className="animate-spin" />
                ) : null}
              </span>
              <span className={state === "pending" ? "text-mulberry/55" : "text-oxblood"}>
                {STAGE_LABEL[stage]}
              </span>
            </li>
          );
        })}
      </ol>

      <button
        onClick={onCancel}
        className="mt-6 w-full text-[12px] text-mulberry/70 hover:text-oxblood transition"
      >
        Cancel
      </button>
    </motion.div>
  );
}

function SuccessBlock() {
  return (
    <motion.div
      key="ok"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      className="py-4 text-center"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className="mx-auto h-14 w-14 rounded-full flex items-center justify-center"
        style={{ background: "linear-gradient(135deg, #C7886B, #5C1E2A)" }}
      >
        <Check className="text-parchment" size={26} />
      </motion.div>
      <div className="mt-4 text-[15px] text-oxblood font-medium">Account connected</div>
      <div className="text-[12px] text-mulberry/70 mt-1">Opening your repositories…</div>
    </motion.div>
  );
}

function ErrorBlock({
  kind,
  message,
  onRetry,
}: {
  kind: ErrorKind;
  message: string;
  onRetry: () => void;
}) {
  const meta = {
    network: {
      Icon: WifiOff,
      title: "Network error",
      body: "We couldn't reach GitHub. Check your connection and try again.",
    },
    unauthorized: {
      Icon: Shield,
      title: "Unauthorized",
      body: "Atlas isn't authorized on your GitHub account.",
    },
    expired: {
      Icon: AlertCircle,
      title: "Session expired",
      body: "Your GitHub session expired mid-flow.",
    },
    generic: {
      Icon: AlertCircle,
      title: "Authorization failed",
      body: "Something went wrong during sign-in.",
    },
  }[kind];
  const { Icon } = meta;
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
    >
      <div className="flex gap-3 p-4 rounded-2xl bg-[#792E3C]/8 border border-[#792E3C]/20">
        <div className="h-9 w-9 rounded-xl bg-burgundy/15 text-burgundy flex items-center justify-center shrink-0">
          <Icon size={17} />
        </div>
        <div className="min-w-0">
          <div className="text-[14px] font-medium text-oxblood">{meta.title}</div>
          <div className="text-[12.5px] text-mulberry/85 mt-1 leading-relaxed">
            {message || meta.body}
          </div>
        </div>
      </div>
      <button
        onClick={onRetry}
        className="mt-5 w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-parchment text-[13.5px] font-medium hover:bg-burgundy transition"
      >
        <RefreshCw size={14} /> Try again
      </button>
      <a
        href="https://docs.github.com/en/apps/oauth-apps/using-oauth-apps/authorizing-oauth-apps"
        target="_blank"
        rel="noreferrer"
        className="mt-3 block text-center text-[11.5px] text-mulberry/65 hover:text-oxblood transition"
      >
        Learn more about GitHub OAuth →
      </a>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Profile panel (post sign-in)
// ---------------------------------------------------------------------------
function ProfilePanel({
  profile,
  onDisconnect,
  onSwitch,
}: {
  profile: GitHubProfile;
  onDisconnect: () => void;
  onSwitch: () => void;
}) {
  const pinned = useApiQuery((s) => GitHubService.listPinned(s), []);
  const recent = useApiQuery((s) => GitHubService.listRecent(s), []);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshed, setRefreshed] = useState<null | number>(null);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const res = await GitHubService.refreshRepositories();
      setRefreshed(res.refreshed);
      pinned.refetch();
      recent.refetch();
    } finally {
      setRefreshing(false);
      setTimeout(() => setRefreshed(null), 2000);
    }
  }

  const stats = useMemo(
    () => [
      { label: "Followers", value: profile.followers },
      { label: "Following", value: profile.following },
      { label: "Public repos", value: profile.publicRepos },
      { label: "Private repos", value: profile.privateRepos },
    ],
    [profile],
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.4 }}
      className="acrylic-strong rounded-3xl p-7"
      style={{ boxShadow: "0 30px 60px -30px rgba(92,30,42,0.35)" }}
    >
      <div className="flex items-start gap-4">
        <div className="relative">
          <img
            src={profile.avatarUrl}
            alt={profile.login}
            className="h-14 w-14 rounded-2xl object-cover ring-2 ring-oxblood/15"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
          <span className="sr-only">{initials(profile.name)}</span>
          <span className="absolute -bottom-1 -right-1 h-5 px-1.5 rounded-full bg-[#5C7C4A] text-parchment text-[10px] font-medium flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-parchment" /> Live
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-serif text-[22px] text-oxblood leading-tight truncate">
            {profile.name}
          </div>
          <a
            href={profile.htmlUrl}
            target="_blank"
            rel="noreferrer"
            className="text-[13px] text-mulberry/75 hover:text-oxblood transition"
          >
            @{profile.login}
          </a>
          {profile.bio && (
            <p className="mt-2 text-[13px] text-mulberry/80 leading-relaxed">{profile.bio}</p>
          )}
        </div>
      </div>

      <div className="mt-5 grid grid-cols-4 gap-2">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-oxblood/10 bg-parchment/40 px-3 py-2.5 text-center"
          >
            <div className="font-serif text-[20px] text-oxblood leading-none">
              {s.value.toLocaleString()}
            </div>
            <div className="mt-1 text-[10.5px] font-mono uppercase tracking-[0.14em] text-mulberry/60">
              {s.label}
            </div>
          </div>
        ))}
      </div>

      {profile.organizations.length > 0 && (
        <div className="mt-5">
          <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-mulberry/55 mb-2 flex items-center gap-2">
            <Users size={12} /> Organizations
          </div>
          <div className="flex flex-wrap gap-1.5">
            {profile.organizations.map((o) => (
              <span
                key={o.login}
                className="text-[12px] px-2.5 py-1 rounded-full bg-oxblood/[0.05] border border-oxblood/10 text-oxblood"
              >
                {o.name}
              </span>
            ))}
          </div>
        </div>
      )}

      <RepoStrip title="Pinned" repos={pinned.data ?? []} loading={pinned.loading} />
      <RepoStrip title="Recent" repos={recent.data ?? []} loading={recent.loading} />

      <div className="mt-6 grid grid-cols-3 gap-2">
        <Link
          to="/explore"
          className="col-span-3 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-oxblood text-parchment text-[13.5px] font-medium hover:bg-burgundy transition"
          style={{
            boxShadow: "inset 0 1px 0 rgba(240,230,177,0.2), 0 12px 30px -12px rgba(92,30,42,0.6)",
          }}
        >
          Continue to Explorer <ArrowRight size={15} />
        </Link>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-[12.5px] text-oxblood border border-oxblood/12 bg-parchment/50 hover:border-oxblood/30 transition disabled:opacity-60"
        >
          {refreshing ? <Loader2 size={13} className="animate-spin" /> : <RefreshCw size={13} />}
          {refreshed != null ? `${refreshed} synced` : "Refresh"}
        </button>
        <button
          onClick={onSwitch}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-[12.5px] text-oxblood border border-oxblood/12 bg-parchment/50 hover:border-oxblood/30 transition"
        >
          <GitBranch size={13} /> Switch
        </button>
        <button
          onClick={onDisconnect}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-[12.5px] text-mulberry/80 hover:text-burgundy hover:bg-burgundy/8 transition"
        >
          <LogOut size={13} /> Disconnect
        </button>
      </div>
    </motion.div>
  );
}

function RepoStrip({
  title,
  repos,
  loading,
}: {
  title: string;
  repos: RepositorySummary[];
  loading: boolean;
}) {
  return (
    <div className="mt-5">
      <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-mulberry/55 mb-2">
        {title} repositories
      </div>
      {loading ? (
        <div className="space-y-1.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-9 rounded-lg bg-oxblood/[0.05] animate-pulse" />
          ))}
        </div>
      ) : repos.length === 0 ? (
        <div className="text-[12px] text-mulberry/60">Nothing yet.</div>
      ) : (
        <ul className="space-y-1">
          {repos.slice(0, 4).map((r) => (
            <li key={r.id}>
              <Link
                to="/repository/$id"
                params={{ id: r.id }}
                className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-oxblood/[0.05] transition group"
              >
                <img
                  src={r.ownerAvatarUrl}
                  alt=""
                  className="h-6 w-6 rounded-md ring-1 ring-oxblood/10"
                  onError={(e) => (e.currentTarget.style.display = "none")}
                />
                <div className="min-w-0 flex-1">
                  <div className="text-[13px] text-oxblood truncate">
                    <span className="text-mulberry/60">{r.owner}/</span>
                    <span className="font-medium">{r.name}</span>
                  </div>
                  <div className="text-[11px] text-mulberry/60 truncate">{r.description}</div>
                </div>
                <span
                  className="text-[10.5px] px-1.5 py-0.5 rounded-full border"
                  style={{ borderColor: `${r.languageColor}55`, color: r.languageColor }}
                >
                  {r.language}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function GitHubMark({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.09.68-.22.68-.49v-1.7c-2.78.62-3.37-1.35-3.37-1.35-.45-1.17-1.11-1.48-1.11-1.48-.91-.63.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.27 2.75 1.05a9.4 9.4 0 0 1 5 0c1.91-1.32 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9v2.82c0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2z" />
    </svg>
  );
}
