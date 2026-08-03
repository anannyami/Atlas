from models.analysis import RepositoryDNA
from models.knowledge import RepositoryKnowledge
from models.evidence import RepositoryEvidence
from services.evidence.extractor import EvidenceExtractor


class RepositoryDNAAnalyzer:

    def __init__(self):
        self.extractor = EvidenceExtractor()

    def analyze(
        self,
        knowledge: RepositoryKnowledge,
    ) -> RepositoryDNA:

        evidence = self.extractor.extract(knowledge)

        return RepositoryDNA(
            traits=self._detect_traits(evidence),
            strengths=self._detect_strengths(evidence),
            engineering_style=self._engineering_style(evidence),
            maturity=self._detect_maturity(evidence),
            confidence=self._confidence(evidence),
        )