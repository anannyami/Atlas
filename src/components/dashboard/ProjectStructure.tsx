import { useAnalysis } from "@/context/AnalysisContext";

export default function ProjectStructure() {
  const { structure } = useAnalysis();

  if (!structure) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          No repository structure available.
        </div>
      </section>
    );
  }

  const stats = [
    {
      title: "Total Files",
      value: structure.total_files,
    },
    {
      title: "Directories",
      value: structure.total_directories,
    },
    {
      title: "Maximum Depth",
      value: structure.max_depth,
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Repository Structure</h2>

        <p className="mt-2 text-mulberry">
          Overview of the repository organization and directory layout.
        </p>
      </div>

      {/* Statistics */}
      <div className="grid gap-6 md:grid-cols-3">
        {stats.map((stat) => (
          <div
            key={stat.title}
            className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm"
          >
            <h3 className="text-sm uppercase tracking-widest text-mulberry/70">{stat.title}</h3>

            <p className="mt-4 text-3xl font-semibold text-oxblood">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Major Directories */}
      <div className="mt-10 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood">Major Directories</h3>

        <p className="mt-2 text-sm text-mulberry">Primary folders detected in the repository.</p>

        <div className="mt-6 flex flex-wrap gap-3">
          {structure.major_directories.length > 0 ? (
            structure.major_directories.map((directory) => (
              <span
                key={directory}
                className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy"
              >
                {directory}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No major directories detected.</span>
          )}
        </div>
      </div>
    </section>
  );
}
