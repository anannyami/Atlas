import { useAnalysis } from "@/context/AnalysisContext";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border/40 py-2">
      <span className="font-medium text-muted-foreground">{label}</span>
      <span className="text-right">{value}</span>
    </div>
  );
}

export default function RepositoryOverview() {
  const { repository, tech_stack, classification } = useAnalysis();

  if (!repository || !tech_stack || !classification) {
    return <div className="text-center py-20">No repository selected.</div>;
  }

  const format = (items: string[]) => (items.length ? items.join(", ") : "Not detected");

  return (
    <section className="rounded-xl border bg-card p-6 shadow-sm">
      <h2 className="text-2xl font-bold mb-6">Repository Overview</h2>

      <div className="space-y-1">
        <InfoRow label="Languages" value={format(tech_stack.languages)} />

        <InfoRow label="Frontend" value={format(tech_stack.frontend)} />

        <InfoRow label="Backend" value={format(tech_stack.backend)} />

        <InfoRow label="Database" value={format(tech_stack.database)} />

        <InfoRow label="Cloud" value={format(tech_stack.cloud)} />

        <InfoRow label="CI / CD" value={format(tech_stack.ci_cd)} />

        <InfoRow label="Containers" value={format(tech_stack.containers)} />

        <InfoRow label="Package Managers" value={format(tech_stack.package_managers)} />

        <InfoRow label="Mobile" value={format(tech_stack.mobile)} />

        <InfoRow label="Project Type" value={classification.project_type} />
      </div>
    </section>
  );
}
