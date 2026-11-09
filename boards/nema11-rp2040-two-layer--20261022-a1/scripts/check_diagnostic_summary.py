"""Treat native source warnings as unresolved; never infer acceptance from exit 0."""
import argparse
import json
from pathlib import Path
import re


def analyze(text, native_exit):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    errors = re.findall(r'^Errors:\s*(\d+)\s*$', text, re.M)
    warnings = re.findall(r'^Warnings:\s*(\d+)\s*$', text, re.M)
    recognized = len(errors) == len(warnings) == 1
    exception = bool(re.search(r'Async effect error|AutorouterError:|\b(?:TypeError|ReferenceError|SyntaxError):', text))
    return {'native_exit': native_exit, 'recognized_summary': recognized,
            'errors': int(errors[0]) if len(errors) == 1 else None,
            'warnings': int(warnings[0]) if len(warnings) == 1 else None,
            'internal_exception': exception, 'accepted_warnings': [],
            'passed': recognized and native_exit == 0 and errors == ['0'] and warnings == ['0'] and not exception}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--native-exit', required=True, type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = analyze(args.log.read_text(), args.native_exit)
    report['log'] = str(args.log)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
