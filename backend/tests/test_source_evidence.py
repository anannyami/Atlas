import sys
import unittest
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.github_client import GitHubAPIError
from services.analysis_service import AnalysisService
from services.github_service import GitHubService
from core.config import Settings


class SourceEvidenceTests(unittest.TestCase):
    def test_source_evidence_settings_use_current_defaults(self) -> None:
        config = Settings(_env_file=None)
        service = AnalysisService(config=config)

        self.assertEqual(service.source_max_files, 40)
        self.assertEqual(service.source_max_file_bytes, 16_000)
        self.assertEqual(service.source_max_total_bytes, 240_000)
        self.assertEqual(service.source_max_concurrency, 5)

    def test_custom_source_evidence_settings_are_enforced(self) -> None:
        config = Settings(
            _env_file=None,
            SOURCE_MAX_FILES=1,
            SOURCE_MAX_FILE_BYTES=8,
            SOURCE_MAX_TOTAL_BYTES=8,
            SOURCE_MAX_CONCURRENCY=2,
        )
        service = AnalysisService(config=config)
        tree = [
            {"path": "a.py", "type": "blob", "size": 8},
            {"path": "b.py", "type": "blob", "size": 8},
        ]

        paths, notes = service.select_source_paths(tree)
        evidence, evidence_notes = service._build_source_evidence(
            {"a.py": "123456789", "b.py": "ok"},
            "",
        )

        self.assertEqual(paths, ["a.py"])
        self.assertTrue(any("bounded to 1 files" in note for note in notes))
        self.assertEqual([item.path for item in evidence], ["a.py"])
        self.assertTrue(evidence[0].truncated)
        self.assertTrue(any("a.py" in note for note in evidence_notes))

    def test_source_evidence_settings_can_be_configured_by_environment(self) -> None:
        values = {
            "SOURCE_MAX_FILES": "3",
            "SOURCE_MAX_FILE_BYTES": "4096",
            "SOURCE_MAX_TOTAL_BYTES": "8192",
            "SOURCE_MAX_CONCURRENCY": "2",
        }
        with patch.dict(os.environ, values):
            config = Settings(_env_file=None)

        self.assertEqual(
            (
                config.SOURCE_MAX_FILES,
                config.SOURCE_MAX_FILE_BYTES,
                config.SOURCE_MAX_TOTAL_BYTES,
                config.SOURCE_MAX_CONCURRENCY,
            ),
            (3, 4096, 8192, 2),
        )

    def test_source_evidence_settings_reject_invalid_values_and_hard_cap_values(self) -> None:
        with self.assertRaises(ValueError):
            Settings(_env_file=None, SOURCE_MAX_FILES=0)
        with self.assertRaises(ValueError):
            Settings(_env_file=None, SOURCE_MAX_FILE_BYTES=1_048_577)
        with self.assertRaises(ValueError):
            Settings(_env_file=None, SOURCE_MAX_TOTAL_BYTES=5_242_881)
        with self.assertRaises(ValueError):
            Settings(_env_file=None, SOURCE_MAX_CONCURRENCY=21)

    def test_default_source_selection_remains_bounded(self) -> None:
        service = AnalysisService(config=Settings(_env_file=None))
        tree = [
            {"path": f"src/file_{index}.py", "type": "blob", "size": 100}
            for index in range(60)
        ]

        paths, _ = service.select_source_paths(tree)

        self.assertLessEqual(len(paths), 40)

    def test_select_source_paths_is_bounded_and_excludes_secrets_generated_and_locks(self) -> None:
        tree = [
            {"path": "README.md", "type": "blob", "size": 100},
            {"path": "backend/app.py", "type": "blob", "size": 100},
            {"path": "tests/test_app.py", "type": "blob", "size": 100},
            {"path": "docs/flow.md", "type": "blob", "size": 100},
            {"path": ".env", "type": "blob", "size": 100},
            {"path": "package-lock.json", "type": "blob", "size": 100},
            {"path": "dist/bundle.js", "type": "blob", "size": 100},
            {"path": "vendor/library.py", "type": "blob", "size": 100},
            {"path": "backend/generated.py", "type": "blob", "size": 100},
            {"path": "large.py", "type": "blob", "size": 20_000},
        ]

        service = AnalysisService(config=Settings(_env_file=None))
        paths, notes = service.select_source_paths(tree)

        self.assertEqual(paths, ["README.md", "docs/flow.md", "tests/test_app.py", "backend/app.py"])
        self.assertTrue(any("large.py" in note for note in notes))
        self.assertNotIn(".env", paths)
        self.assertNotIn("package-lock.json", paths)

    def test_build_source_evidence_records_lines_and_truncation(self) -> None:
        service = AnalysisService(config=Settings(_env_file=None))
        evidence, notes = service._build_source_evidence(
            {"src/app.py": "one\ntwo\nthree", "docs/guide.md": "guide", "large.py": "x" * 17_000},
            "",
        )

        app = next(item for item in evidence if item.path == "src/app.py")
        self.assertEqual((app.start_line, app.end_line), (1, 3))
        self.assertEqual(app.text, "one\ntwo\nthree")
        self.assertFalse(app.truncated)
        large = next(item for item in evidence if item.path == "large.py")
        self.assertTrue(large.truncated)
        self.assertTrue(any("large.py" in note for note in notes))

    def test_github_authentication_errors_are_not_silently_discarded(self) -> None:
        service = GitHubService.__new__(GitHubService)
        service.github = type("Client", (), {})()
        service.github.get = AsyncMock(side_effect=GitHubAPIError(401, "Invalid GitHub token."))

        async def run() -> None:
            with self.assertRaises(GitHubAPIError):
                await service.get_file_content("owner", "repo", "secret.py")

        import asyncio
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
