"""Turn reported native schematic-placement findings into a strict local gate."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('native_log', type=Path)
parser.add_argument('--native-exit', type=int, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
text = args.native_log.read_text()
issues = []
parse_errors = []
for block in re.findall(r'<SchematicPlacementIssues\b[^>]*>.*?</SchematicPlacementIssues>', text, re.S):
    try:
        issues.extend({'kind':element.tag,'attributes':element.attrib} for element in ET.fromstring(block))
    except ET.ParseError as error:
        parse_errors.append(str(error))
exception = 'Async effect error' in text or 'AutorouterError:' in text
passed = args.native_exit == 0 and not issues and not parse_errors and not exception
report = {'native_log':str(args.native_log),'native_exit':args.native_exit,'reported_issue_count':len(issues),'issue_kinds':dict(Counter(x['kind'] for x in issues)),'issues':issues,'parse_errors':parse_errors,'internal_exception_present':exception,'strict_gate_passed':passed,'scope':'Additional gate after the required unchanged native CLI command; no findings waived or suppressed'}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['issues']},indent=2))
raise SystemExit(0 if passed else 1)
