import { useAnalysis } from "@/context/AnalysisContext";

function confidenceLabel(value: number) {
  return `${Math.round(value * 100)}%`;
}

export default function ProjectClassification() {
  const { classification } = useAnalysis();

  if (!classification) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          Project classification unavailable.
        </div>
      </section>
    );
  }

  const secondary = classification.secondary_classifications ?? [];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-10 shadow-sm">
        <div className="mb-4">
          <h2 className="text-3xl font-serif text-oxblood">Project Classification</h2>

          <p className="mt-2 text-mulberry">
            Atlas analyzed the repository structure, technologies and metadata to identify the most
            likely project category.
          </p>
        </div>

        <div className="rounded-2xl border border-oxblood/10 bg-white/60 p-6">
          <p className="text-sm uppercase tracking-widest text-mulberry/70">Primary</p>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <span className="rounded-full bg-burgundy/10 px-6 py-3 text-xl font-semibold text-burgundy">
              {classification.primary_classification || classification.project_type}
            </span>
            <span className="text-sm text-mulberry">Confidence {confidenceLabel(classification.confidence)}</span>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {secondary.length > 0 ? (
            secondary.map((item) => (
              <div
                key={item.name}
                className="rounded-xl border border-oxblood/10 bg-white/50 p-5 shadow-sm"
              >
                <div className="flex items-center justify-between gap-4">
                  <h3 className="font-medium text-oxblood">{item.name}</h3>
                  <span className="text-sm text-mulberry">{confidenceLabel(item.confidence)}</span>
                </div>
                {item.evidence.length > 0 ? (
                  <p className="mt-3 text-sm text-mulberry">{item.evidence.join(" • ")}</p>
                ) : null}
              </div>
            ))
          ) : (
            <div className="rounded-xl border border-oxblood/10 bg-white/50 p-5 text-mulberry">
              No secondary classifications detected.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
