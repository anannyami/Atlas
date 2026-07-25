import { useAnalysis } from "@/context/AnalysisContext";

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

        <div className="mt-8 flex justify-center">
          <div className="rounded-full bg-burgundy/10 px-8 py-4">
            <span className="text-2xl font-semibold text-burgundy">
              {classification.project_type}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
