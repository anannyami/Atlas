from models.analysis import ProductIdentity
from models.evidence import RepositoryEvidence
from models.knowledge import RepositoryKnowledge
from services.evidence.extractor import EvidenceExtractor
from services.knowledge.product_patterns import PRODUCT_PATTERNS
from services.readme.readme_parser import ReadmeParser


class ProductIdentityAnalyzer:

    def __init__(self):
        self.extractor = EvidenceExtractor()
        self.readme_parser = ReadmeParser()

    def _classify(
        self,
        evidence: RepositoryEvidence,
        readme,
    ):

        readme_text = " ".join(
            [
                readme.title,
                readme.tagline,
                readme.description,
            ]
        ).lower()
        
        description = evidence.description.lower()
        title = evidence.title.lower()
        topics = " ".join(evidence.topics).lower()

        combined_text = " ".join(
            [
                title,
                description,
                topics,
            ]
        )

        readme_text = readme

        best_score = -1
        best_category = "Software"
        best_subcategory = "Unknown"
        matched_keywords = []

        for product in PRODUCT_PATTERNS:

            score = 0
            matches = []

            for keyword, weight in product["keywords"].items():

                key = keyword.lower()

                if key in readme_text:
                    score += weight * 3
                    matches.append(keyword)

                elif key in description:
                    score += weight * 2
                    matches.append(keyword)

                elif key in title:
                    score += weight * 2
                    matches.append(keyword)

                elif key in topics:
                    score += weight * 2
                    matches.append(keyword)

                elif key in combined_text:
                    score += weight
                    matches.append(keyword)

                if product["subcategory"] == "AI Collaboration Platform":

                    if (
                        "humans and agents" in readme_text
                        or "humans & agents" in readme_text
                    ):
                        score += 50

                    if "build together" in readme_text:
                        score += 40

                    if "relay" in readme_text:
                        score += 20

            if score > best_score:
                best_score = score
                best_category = product["category"]
                best_subcategory = product["subcategory"]
                matched_keywords = matches

        return (
            best_category,
            best_subcategory,
            matched_keywords,
        )

    def _build_summary(
        self,
        readme,
        evidence: RepositoryEvidence,
        subcategory: str,
    ) -> str:

        if readme.tagline:
            return readme.tagline

        if readme.description:
            return readme.description

        if evidence.description.strip():
            return evidence.description.strip()

        return f"This repository appears to be a {subcategory.lower()}."
    
    def _confidence(
        self,
        evidence: RepositoryEvidence,
        matched_keywords: list[str],
    ):

        score = 0.0

        if evidence.title:
            score += 0.15

        if evidence.description:
            score += 0.20

        if evidence.readme:
            score += 0.30

        if evidence.topics:
            score += 0.10

        score += min(len(matched_keywords) * 0.05, 0.25)

        return round(min(score, 1.0), 2)

    def analyze(
        self,
        knowledge: RepositoryKnowledge,
    ) -> ProductIdentity:

        evidence = self.extractor.extract(knowledge)
        readme = self.readme_parser.parse(
            evidence.readme,
        )

        category, subcategory, keywords = self._classify(
            evidence,
            readme,
        )

        return ProductIdentity(
            category=category,
            subcategory=subcategory,
            title=subcategory,
            summary=self._build_summary(
                readme,
                evidence,
                subcategory,
            ),
            confidence=self._confidence(
                evidence,
                keywords,
            ),
            evidence=keywords,
        )