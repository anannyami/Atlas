import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.analyzers.classification import ProjectClassificationAnalyzer


class ClassificationTests(unittest.TestCase):
    def test_classification_prefers_app_over_infrastructure_for_react_repo(self):
        analyzer = ProjectClassificationAnalyzer()
        result = analyzer.analyze(
            tree=[{"path": "src/app.tsx"}, {"path": "package.json"}],
            tech_stack={
                "frontend": ["React", "Vite"],
                "backend": [],
                "containers": [],
                "cloud": [],
                "ci_cd": ["GitHub Actions"],
                "languages": ["JavaScript"],
                "technologies": [
                    {"name": "React", "category": "frontend"},
                    {"name": "Vite", "category": "frontend"},
                    {"name": "GitHub Actions", "category": "ci_cd"},
                ],
            },
        )

        self.assertEqual(result["primary_classification"], "Web Application")
        self.assertGreaterEqual(result["confidence"], 0.7)


if __name__ == "__main__":
    unittest.main()
