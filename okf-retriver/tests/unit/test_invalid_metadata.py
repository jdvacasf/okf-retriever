import tempfile
import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


class InvalidMetadataTests(unittest.TestCase):
    def test_invalid_standard_metadata_does_not_abort_build(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.md"
            path.write_text("---\nstatus: [bad]\ntags: invalid\n---\n# Usable\nbody\n")
            index = OKFContextIndex.build(OKFContextConfig(Path(directory)))
            self.assertIn("invalid", index.concepts)
            self.assertTrue(any(item.kind == "INVALID_METADATA" for item in index.diagnostics))

    def test_inconsistent_lexical_snapshot_is_rejected(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        index = OKFContextIndex.build(OKFContextConfig(root))
        index.concept_lexical.documents.pop(next(iter(index.concept_lexical.documents)))
        from okf_context import OKFRetriever
        from okf_context.exceptions import ErrorCode, OKFError
        with self.assertRaises(OKFError) as error:
            OKFRetriever(index, OKFContextConfig(root)).search_context(query="authentication")
        self.assertEqual(error.exception.code, ErrorCode.LEXICAL_INDEX_NOT_READY)
