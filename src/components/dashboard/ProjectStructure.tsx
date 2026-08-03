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
    { title: "Total Files", value: structure.total_files },
    { title: "Directories", value: structure.total_directories },
    { title: "Maximum Depth", value: structure.max_depth },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Repository Structure</h2>

        <p className="mt-2 text-mulberry">
          Overview of the repository organization and directory layout.
        </p>
      </div>

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

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Largest Directories</h3>
          <div className="mt-4 space-y-3">
            {structure.largest_directories.length > 0 ? (
              structure.largest_directories.map((item) => (
                <div key={item.path} className="flex items-center justify-between rounded-xl border border-oxblood/10 bg-white/60 p-4">
                  <span className="text-mulberry font-medium">{item.path}</span>
                  <span className="text-sm text-burgundy">{item.file_count} files</span>
                </div>
              ))
            ) : (
              <p className="text-mulberry">No directory size data available.</p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Deepest Paths</h3>
          <div className="mt-4 space-y-3">
            {structure.deepest_paths.length > 0 ? (
              structure.deepest_paths.map((item) => (
                <div key={item.path} className="flex items-center justify-between rounded-xl border border-oxblood/10 bg-white/60 p-4">
                  <span className="text-mulberry font-medium">{item.path}</span>
                  <span className="text-sm text-burgundy">Depth {item.depth}</span>
                </div>
              ))
            ) : (
              <p className="text-mulberry">No deep path data available.</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Entry Points</h3>
          <div className="mt-4 flex flex-wrap gap-3">
            {structure.entry_points.length > 0 ? (
              structure.entry_points.map((item) => (
                <span key={item} className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy">
                  {item}
                </span>
              ))
            ) : (
              <p className="text-mulberry">No obvious entry points detected.</p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-oxblood">Configuration Files</h3>
          <div className="mt-4 flex flex-wrap gap-3">
            {structure.configuration_files.length > 0 ? (
              structure.configuration_files.map((item) => (
                <span key={item} className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy">
                  {item}
                </span>
              ))
            ) : (
              <p className="text-mulberry">No configuration files detected.</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-10 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood">Tree Intelligence</h3>

        <p className="mt-3 text-mulberry">{structure.summary || "No summarized tree intelligence available."}</p>

        <div className="mt-6 flex flex-wrap gap-3">
          {structure.important_folders.length > 0 ? (
            structure.important_folders.map((item) => (
              <span key={item} className="rounded-full bg-burgundy/10 px-4 py-2 text-sm font-medium text-burgundy">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No important folders detected.</span>
          )}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          {structure.root_technologies.length > 0 ? (
            structure.root_technologies.map((item) => (
              <span key={item} className="rounded-full bg-secondary px-4 py-2 text-sm text-foreground">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No root technologies detected.</span>
          )}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          {structure.major_modules.length > 0 ? (
            structure.major_modules.map((item) => (
              <span key={item} className="rounded-full bg-secondary/80 px-4 py-2 text-sm text-foreground">
                {item}
              </span>
            ))
          ) : (
            <span className="text-mulberry">No major modules detected.</span>
          )}
        </div>
      </div>
    </section>
  );
}
