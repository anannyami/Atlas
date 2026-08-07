import { useAnalysis } from "@/context/AnalysisContext";

export default function Activity() {
  const { activity } = useAnalysis();

  if (!activity) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          Repository activity unavailable.
        </div>
      </section>
    );
  }

  const metrics = [
    { title: "Stars", value: activity.stars },
    { title: "Forks", value: activity.forks },
    { title: "Watchers", value: activity.watchers },
    { title: "Open Issues", value: activity.open_issues },
    { title: "Recent Commits", value: activity.recent_commits },
    { title: "Pull Requests", value: activity.recent_pull_requests },
    { title: "Recent Issues", value: activity.recent_issues },
    { title: "Releases", value: activity.releases },
  ];

  const summaries = [
    { title: "Community Size", value: activity.community_size },
    { title: "Activity Level", value: activity.activity_level },
    { title: "Maintenance Status", value: activity.maintenance_status },
    { title: "Repository Maturity", value: activity.repository_maturity },
    { title: "Commit Frequency", value: activity.commit_frequency || "Unknown" },
    { title: "Issue Frequency", value: activity.issue_frequency || "Unknown" },
    { title: "PR Frequency", value: activity.pr_frequency || "Unknown" },
    { title: "Staleness", value: activity.staleness || "Unknown" },
    {
      title: "Last Commit",
      value:
        activity.last_commit_days === null ? "Unknown" : `${activity.last_commit_days} day(s) ago`,
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Repository Activity</h2>

        <p className="mt-2 text-mulberry">Community engagement and repository activity insights.</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div
            key={metric.title}
            className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm"
          >
            <h3 className="text-sm uppercase tracking-widest text-mulberry/70">{metric.title}</h3>

            <p className="mt-4 text-3xl font-semibold text-oxblood">{metric.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood mb-6">Repository Insights</h3>

        <div className="grid gap-4 md:grid-cols-2">
          {summaries.map((item) => (
            <div
              key={item.title}
              className="flex items-center justify-between rounded-xl border border-oxblood/10 bg-white/60 p-4"
            >
              <span className="text-mulberry font-medium">{item.title}</span>

              <span className="font-semibold text-oxblood">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-10 rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-oxblood mb-4">Activity Explanations</h3>

        {(activity.explanations ?? []).length > 0 ? (
          <ul className="space-y-3 text-mulberry">
            {(activity.explanations ?? []).map((item) => (
              <li key={item} className="rounded-xl border border-oxblood/10 bg-white/60 p-4">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-mulberry">No additional explanations were generated.</p>
        )}
      </div>
    </section>
  );
}
