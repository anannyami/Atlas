from models.intelligence import RepositoryKnowledge
from models.analysis import RepositoryInfo


class KnowledgeBuilder:
    def build(
        self,
        *,
        repository,
        readme,
        tree,
        architecture,
        structure,
        tech_stack,
        health,
        activity,
        contributors,
        branches,
        releases,
        issues,
        pull_requests,
    ) -> RepositoryKnowledge:

        return RepositoryKnowledge(
            repository=repository,

            readme=readme,

            tree=tree,

            architecture=architecture,
            structure=structure,
            tech_stack=tech_stack,
            health=health,
            activity=activity,

            contributors=contributors,
            branches=branches,
            releases=releases,
            issues=issues,
            pull_requests=pull_requests,
        )