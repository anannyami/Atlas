import { useAnalysis } from "@/context/AnalysisContext";

export default function Activity() {
  const { activity, health, analysisResponse } = useAnalysis();

  if (!activity) {
    return (
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-oxblood/10 bg-white/40 backdrop-blur-md p-8 text-center text-mulberry">
          Repository activity unavailable.
        </div>
      </section>
    );
  }

  const statistics = [
    { title: "Stars", value: activity.stars },
    { title: "Forks", value: activity.forks },
    { title: "Watchers", value: activity.watchers },
    { title: "Open Issues", value: activity.open_issues },
    {
      title: "Days Since Latest Commit",
      value: activity.last_commit_days === null ? "Unknown" : activity.last_commit_days,
    },
    { title: "Pull Requests", value: activity.recent_pull_requests },
    { title: "Releases", value: activity.releases },
  ];

  const contributors = analysisResponse?.knowledge?.contributors ?? [];
  const contributionTotal = contributors.reduce(
    (total, contributor) => total + (contributor.contributions ?? 0),
    0,
  );
  const latestRelease = analysisResponse?.knowledge?.releases?.find(
    (release) => release.published_at || release.created_at,
  );
  const releaseTimestamp = latestRelease?.published_at ?? latestRelease?.created_at;
  const releaseTime = releaseTimestamp ? Date.parse(releaseTimestamp) : Number.NaN;
  const lastReleaseAge = Number.isNaN(releaseTime)
    ? "Unknown"
    : `${Math.max(0, Math.floor((Date.now() - releaseTime) / 86_400_000))} day(s) ago`;

  const insights = [
    { title: "Community Size", value: activity.community_size },
    { title: "Activity Level", value: activity.activity_level },
    { title: "Repository Health", value: health?.overall_status ?? health?.health ?? "Unknown" },
    { title: "Maintenance Status", value: activity.maintenance_status },
    { title: "Repository Maturity", value: activity.repository_maturity },
    { title: "Commit Frequency", value: activity.commit_frequency || "Unknown" },
    {
      title: "Development Velocity",
      value: `${activity.commit_frequency || "Unknown"} commits / ${activity.pr_frequency || "Unknown"} PRs`,
    },
    { title: "Issue Frequency", value: activity.issue_frequency || "Unknown" },
    { title: "PR Frequency", value: activity.pr_frequency || "Unknown" },
    { title: "Staleness", value: activity.staleness || "Unknown" },
    { title: "Last Release Age", value: lastReleaseAge },
    {
      title: "Contributor Activity",
      value: `${contributors.length} returned; ${contributionTotal} recorded contributions`,
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-serif text-oxblood">Repository Activity</h2>

        <p className="mt-2 text-mulberry">
          GitHub repository statistics and Atlas-generated engineering insights.
        </p>
      </div>

      <h3 className="mb-4 text-xl font-semibold text-oxblood">Repository Statistics</h3>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statistics.map((metric) => (
          <div
            key={metric.title}
            className="rounded-2xl border border-oxblood/10 bg-white/50 backdrop-blur-md p-6 shadow-sm"
          >
            <h3 className="text-sm uppercase tracking-widest text-mulberry/70">{metric.title}</h3>

            <p className="mt-4 text-3xl font-semibold text-oxblood">{metric.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-10">
        <h3 className="mb-6 text-xl font-semibold text-oxblood">Repository Activity Insights</h3>

        <div className="grid gap-4 md:grid-cols-2">
          {insights.map((item) => (
            <div
              key={item.title}
              className="flex items-center justify-between gap-4 rounded-xl border border-oxblood/10 bg-white/50 p-4"
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
