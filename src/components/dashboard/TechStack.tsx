import { useAnalysis } from "@/context/AnalysisContext";

export default function TechStack() {
  const { techStack } = useAnalysis();

  if (!techStack) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-8">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          No technology stack detected.
        </div>
      </section>
    );
  }

  const cards = [
    {
      title: "Languages",
      values: techStack.languages.length > 0 ? techStack.languages : ["Not detected"],
    },
    {
      title: "Frontend",
      values: techStack.frontend.length > 0 ? techStack.frontend : ["Not detected"],
    },
    {
      title: "Backend",
      values: techStack.backend.length > 0 ? techStack.backend : ["Not detected"],
    },
    {
      title: "Database",
      values: techStack.database.length > 0 ? techStack.database : ["Not detected"],
    },
    {
      title: "Cloud",
      values: techStack.cloud.length > 0 ? techStack.cloud : ["Not detected"],
    },
    {
      title: "CI / CD",
      values: techStack.ci_cd.length > 0 ? techStack.ci_cd : ["Not detected"],
    },
    {
      title: "Package Managers",
      values: techStack.package_managers.length > 0 ? techStack.package_managers : ["Not detected"],
    },
    {
      title: "Containers",
      values: techStack.containers.length > 0 ? techStack.containers : ["Not detected"],
    },
    {
      title: "Mobile",
      values: techStack.mobile.length > 0 ? techStack.mobile : ["Not detected"],
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Technology Stack</h2>

        <p className="mt-2 text-mulberry">Technologies detected from the repository.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.title}
            className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm"
          >
            <h3 className="text-sm uppercase tracking-widest text-mulberry/70">{card.title}</h3>

            <div className="mt-4 flex flex-wrap gap-2">
              {card.values.map((item) => (
                <span
                  key={item}
                  className="rounded-full bg-burgundy/10 px-3 py-1 text-sm text-burgundy"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
