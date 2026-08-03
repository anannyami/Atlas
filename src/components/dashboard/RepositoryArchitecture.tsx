import { useAnalysis } from "@/context/AnalysisContext";

function SignalGroup({ title, items }: { title: string; items: { name: string; confidence: number; evidence: string[] }[] }) {
  return (
    <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
      <h3 className="text-xl font-semibold text-oxblood">{title}</h3>
      <div className="mt-4 space-y-3">
        {items.length > 0 ? (
          items.map((item) => (
            <div key={item.name} className="rounded-xl border border-oxblood/10 bg-white/60 p-4">
              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-oxblood">{item.name}</span>
                <span className="text-sm text-mulberry">{Math.round(item.confidence * 100)}%</span>
              </div>
              {item.evidence.length > 0 ? (
                <p className="mt-2 text-sm text-mulberry">{item.evidence.join(" • ")}</p>
              ) : null}
            </div>
          ))
        ) : (
          <p className="text-mulberry">No detections available.</p>
        )}
      </div>
    </div>
  );
}

export default function RepositoryArchitecture() {
  const { architecture } = useAnalysis();

  if (!architecture) {
    return null;
  }

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Architecture Analysis</h2>

        <p className="mt-2 text-mulberry">
          Heuristic architectural interpretation of the repository structure and dependencies.
        </p>
      </div>

      <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-8 shadow-sm">
        <div className="flex flex-wrap items-center gap-4">
          <span className="rounded-full bg-burgundy/10 px-6 py-3 text-xl font-semibold text-burgundy">
            {architecture.style}
          </span>
          <span className="text-sm text-mulberry">Confidence {Math.round(architecture.confidence * 100)}%</span>
        </div>
        <p className="mt-4 text-mulberry">{architecture.summary || "No architecture summary available."}</p>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <SignalGroup title="Frontend Frameworks" items={architecture.frontend_frameworks} />
        <SignalGroup title="Backend Frameworks" items={architecture.backend_frameworks} />
        <SignalGroup title="Databases" items={architecture.databases} />
        <SignalGroup title="Cloud" items={architecture.cloud} />
        <SignalGroup title="Authentication" items={architecture.authentication} />
        <SignalGroup title="API Style" items={architecture.api_styles} />
        <SignalGroup title="Architecture Patterns" items={architecture.architecture_patterns} />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Applications</h3>
          <div className="mt-4 flex flex-wrap gap-3">
            {architecture.applications.length > 0 ? (
              architecture.applications.map((item) => (
                <span key={item} className="rounded-full bg-secondary px-4 py-2 text-sm text-foreground">
                  {item}
                </span>
              ))
            ) : (
              <span className="text-mulberry">No application types detected.</span>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Organization</h3>
          <div className="mt-4 flex flex-wrap gap-3">
            {architecture.organization.length > 0 ? (
              architecture.organization.map((item) => (
                <span key={item} className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy">
                  {item}
                </span>
              ))
            ) : (
              <span className="text-mulberry">No organization hints detected.</span>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood">Deployment & Workspace Signals</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          {architecture.workspace.length > 0 ? (
            architecture.workspace.map((item) => (
              <span key={item} className="rounded-full bg-secondary px-4 py-2 text-sm text-foreground">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No workspace signals detected.</span>
          )}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          {architecture.deployment.length > 0 ? (
            architecture.deployment.map((item) => (
              <span key={item} className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No deployment signals detected.</span>
          )}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          {architecture.modules.length > 0 ? (
            architecture.modules.map((item) => (
              <span key={item} className="rounded-full bg-secondary/80 px-4 py-2 text-sm text-foreground">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No module signals detected.</span>
          )}
        </div>
      </div>
    </section>
  );
}
