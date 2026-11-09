"""Native summary controls: warnings and malformed output must block approval."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('summary', Path(__file__).resolve().parents[1] / 'scripts/check_diagnostic_summary.py')
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class NativeSummary(unittest.TestCase):
    def test_clean_output(self):
        self.assertTrue(summary.analyze('Errors: 0\nWarnings: 0\n', 0)['passed'])

    def test_unresolved_warning_blocks_acceptance(self):
        report = summary.analyze('Errors: 0\nWarnings: 30\n', 0)
        self.assertFalse(report['passed'])
        self.assertEqual(report['warnings'], 30)

    def test_missing_duplicate_exception_or_failure_rejected(self):
        for text, code in [('Errors: 0\n', 0), ('Errors: 0\nWarnings: 0\nErrors: 0\n', 0),
                           ('Errors: 0\nWarnings: 0\nTypeError: failure\n', 0),
                           ('Errors: 0\nWarnings: 0\n', 1), ('Errors: 2\nWarnings: 0\n', 0)]:
            with self.subTest(text=text, code=code):
                self.assertFalse(summary.analyze(text, code)['passed'])


if __name__ == '__main__':
    unittest.main()
