import { useAnalysis } from "@/context/AnalysisContext";

function Badge({ text }: { text: string }) {
  return <span className="rounded-full bg-secondary px-3 py-1 text-sm">{text}</span>;
}

export default function RepositoryOverview() {
  const { repository, summary } = useAnalysis();

  if (!repository || !summary) {
    return null;
  }

  return (
    <section className="space-y-8">
      <div>
        <h2 className="text-5xl font-serif">Repository Intelligence</h2>

        <p className="text-muted-foreground mt-2">
          Automatically generated repository understanding.
        </p>
      </div>

      <div className="rounded-2xl border bg-card p-8 space-y-8">
        <div>
          <h3 className="text-xl font-semibold mb-3">Overview</h3>

          <p className="leading-8 text-base">{summary.overview}</p>
        </div>

        <div>
          <h3 className="text-xl font-semibold mb-3">Purpose</h3>

          <p className="leading-8 text-base">{summary.purpose}</p>
        </div>

        <div>
          <h3 className="text-xl font-semibold mb-3">Current Status</h3>

          <p>{summary.current_status}</p>
        </div>

        <div>
          <h3 className="text-xl font-semibold mb-4">Highlights</h3>

          <div className="flex flex-wrap gap-3">
            {(summary.highlights ?? []).map((item) => (
              <Badge key={item} text={item} />
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold mb-4">Summary Sources</h3>

          <div className="flex flex-wrap gap-3">
            {(summary.source_factors ?? []).length > 0 ? (
              (summary.source_factors ?? []).map((item) => <Badge key={item} text={item} />)
            ) : (
              <span className="text-muted-foreground">No source metadata available.</span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
