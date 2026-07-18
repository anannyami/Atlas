import type { Repository } from "@/lib/mock-repositories";
import { RepositoryCard } from "./RepositoryCard";

export function RepositoryGrid({ repositories }: { repositories: Repository[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      {repositories.map((r, i) => (
        <RepositoryCard key={r.id} repo={r} index={i} />
      ))}
    </div>
  );
}
