from models.evidence import RepositoryEvidence
from models.knowledge import RepositoryKnowledge


class EvidenceExtractor:

    def extract(
        self,
        knowledge: RepositoryKnowledge,
    ) -> RepositoryEvidence:

        repository = knowledge.repository

        def dump(value):
            if hasattr(value, "model_dump"):
                return value.model_dump()
            return value

        return RepositoryEvidence(
            title=repository.name,
            description=repository.description or "",

            readme=knowledge.readme,

            topics=repository.topics,

            frontend=knowledge.tech_stack.frontend,
            backend=knowledge.tech_stack.backend,
            databases=knowledge.tech_stack.database,
            cloud=knowledge.tech_stack.cloud,
            cicd=knowledge.tech_stack.ci_cd,

            architecture=dump(knowledge.architecture),
            structure=dump(knowledge.structure),
            health=dump(knowledge.health),
            activity=dump(knowledge.activity),
        )