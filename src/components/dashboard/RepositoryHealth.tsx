import { useAnalysis } from "@/context/AnalysisContext";

export default function RepositoryHealth() {
  const { health } = useAnalysis();

  if (!health) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          Repository health data unavailable.
        </div>
      </section>
    );
  }

  const scoreColor =
    health.score >= 80 ? "text-green-600" : health.score >= 60 ? "text-yellow-600" : "text-red-600";

  const overallStatus = health.overall_status ?? health.health ?? "Unknown";

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Repository Health</h2>

        <p className="mt-2 text-mulberry">
          Overall quality assessment generated from repository analysis.
        </p>
      </div>

      <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-8 shadow-sm">
        <p className="text-sm uppercase tracking-widest text-mulberry/70">Health Score</p>

        <h1 className={`mt-4 text-6xl font-bold ${scoreColor}`}>{health.score}%</h1>
        <p className="mt-3 text-sm text-mulberry">{overallStatus}</p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(health.component_scores).map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-5 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-oxblood capitalize">{label.replace(/_/g, " ")}</h3>
              <span className="text-xl text-burgundy">{value}%</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood mb-4">Individual Checks</h3>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Object.entries(health.checks).map(([check, passed]) => (
            <div
              key={check}
              className="rounded-xl border border-oxblood/10 bg-white/60 p-4"
            >
              <div className="flex items-center justify-between gap-3">
                <h4 className="font-medium text-oxblood capitalize">{check.replace(/_/g, " ")}</h4>
                <span className={`text-xl ${passed ? "text-green-600" : "text-red-600"}`}>
                  {passed ? "✓" : "✗"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood mb-4">Missing Recommendations</h3>

        {health.missing_recommendations.length > 0 ? (
          <ul className="space-y-3 text-mulberry">
            {health.missing_recommendations.map((item) => (
              <li key={item} className="rounded-xl border border-oxblood/10 bg-white/60 p-4">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-mulberry">No major recommendations detected.</p>
        )}
      </div>
    </section>
  );
}
