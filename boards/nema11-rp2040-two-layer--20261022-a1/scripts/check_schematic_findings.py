"""Fail closed on native schematic findings, including truncated XML reports."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def analyze(text, native_exit):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    issues, errors = [], []
    starts = list(re.finditer(r'<Schematic(?:Sheet|PlacementIssues)\b', text))
    # Prefer complete sheets, so malformed outer XML cannot be silently ignored.
    tag = 'SchematicSheet' if '<SchematicSheet' in text else 'SchematicPlacementIssues'
    blocks = re.findall(rf'<{tag}\b[^>]*>.*?</{tag}>|<{tag}\b[^>]*/>', text, re.S)
    expected = len(re.findall(rf'<{tag}\b', text))
    if expected != len(blocks):
        errors.append('Missing or truncated XML report')
    covered = ''.join(blocks)
    for marker in ('SchematicSheet', 'SchematicPlacementIssues'):
        for prefix in ('<', '</'):
            if text.count(prefix + marker) != covered.count(prefix + marker):
                errors.append('Unparsed or truncated ' + marker + ' delimiter')
    for block in blocks:
        try:
            root = ET.fromstring(block)
            containers = [root] if root.tag == 'SchematicPlacementIssues' else list(root.iter('SchematicPlacementIssues'))
            if not containers:
                errors.append('Sheet missing issue container')
            for container in containers:
                issues.extend({'kind': x.tag, 'attributes': x.attrib} for x in container)
        except ET.ParseError as error:
            errors.append(str(error))
    if not starts and not re.search(r'(?:no (?:schematic[- ]placement )?(?:issues|errors|problems)|all checks passed|no schematic placement issues found)', text, re.I):
        errors.append('Unrecognized or empty native report')
    exception = bool(re.search(r'Async effect error|AutorouterError:|\b(?:TypeError|ReferenceError|SyntaxError):', text))
    return {'native_exit': native_exit, 'reported_issue_count': len(issues), 'issue_kinds': dict(Counter(x['kind'] for x in issues)), 'issues': issues, 'parse_errors': errors, 'internal_exception_present': exception, 'strict_gate_passed': native_exit == 0 and not issues and not errors and not exception}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native_log', type=Path)
    parser.add_argument('--native-exit', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = analyze(args.native_log.read_text(), args.native_exit)
    report['native_log'] = str(args.native_log)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['strict_gate_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
