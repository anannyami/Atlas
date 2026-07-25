import { useAnalysis } from "@/context/AnalysisContext";

export default function RepositoryOverview() {
  const { repository } = useAnalysis();

  if (!repository) {
    return <div className="text-center py-20">No repository loaded.</div>;
  }

  return <section>{/* Repository Hero */}</section>;
}
