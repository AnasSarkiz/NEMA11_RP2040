import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('findings', Path(__file__).resolve().parents[1] / 'scripts/native_findings.py')
findings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(findings)


class NestedFindings(unittest.TestCase):
    def test_nested_pad_failure_is_not_hidden_by_grouping(self):
        report = findings.summarize([{'type': 'pcb_footprint_overlap_error', 'related_errors': [
            {'type': 'pcb_pad_pad_clearance_error'},
            {'type': 'pcb_footprint_overlap_error', 'related_errors': [{'type': 'pcb_pad_pad_clearance_error'}]},
        ]}])
        self.assertEqual(report['native_error_count'], 1)
        self.assertEqual(report['native_nested_detail_count'], 3)
        self.assertEqual(report['native_nested_detail_types']['pcb_pad_pad_clearance_error'], 2)

    def test_empty_records_have_no_errors_or_details(self):
        report = findings.summarize([])
        self.assertEqual(report['native_error_count'], 0)
        self.assertEqual(report['native_nested_detail_count'], 0)


if __name__ == '__main__':
    unittest.main()
