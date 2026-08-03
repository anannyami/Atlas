from models.repository_identity import (
    RepositoryIdentity,
    RepositoryIdentityEvidence,
)

from models.knowledge import RepositoryKnowledge

from services.evidence.extractor import EvidenceExtractor
from services.readme.readme_parser import ReadmeParser


class RepositoryIdentityAnalyzer:

    def __init__(self):

        self.extractor = EvidenceExtractor()
        self.readme_parser = ReadmeParser()

    def _collect_evidence(
        self,
        knowledge: RepositoryKnowledge,
    ) -> RepositoryIdentityEvidence:

        readme = self.readme_parser.parse(
            knowledge.readme,
        )

        major_dirs = list(getattr(knowledge.structure, "major_directories", []))

        return RepositoryIdentityEvidence(

            title=readme.title,

            tagline=readme.tagline,

            description=readme.description,

            topics=knowledge.repository.topics,

            frontend=knowledge.tech_stack.frontend,
            backend=knowledge.tech_stack.backend,
            languages=knowledge.tech_stack.languages,
            database=knowledge.tech_stack.database,
            cloud=knowledge.tech_stack.cloud,
            ci_cd=knowledge.tech_stack.ci_cd,
            package_managers=knowledge.tech_stack.package_managers,
            mobile=knowledge.tech_stack.mobile,
            containers=knowledge.tech_stack.containers,

            directories=major_dirs,

            readme_sections=readme.headings,
        )

    def analyze(
        self,
        knowledge: RepositoryKnowledge,
    ) -> RepositoryIdentity:

        evidence = self._collect_evidence(
            knowledge,
        )

        print("\n========== IDENTITY EVIDENCE ==========")
        print(evidence.model_dump())
        print("=======================================\n")

        return RepositoryIdentity(
            product_name=evidence.title,

            category="Unknown",

            subtype="Unknown",

            tagline=evidence.tagline,

            description=evidence.description,

            audience="Unknown",

            capabilities=[],

            confidence=0.0,

            evidence=[],
        )