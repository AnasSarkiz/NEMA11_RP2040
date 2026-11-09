"""Keep grouped native errors and their nested details distinct and visible."""
from collections import Counter


def summarize(records):
    top = [r for r in records if r.get('type', '').endswith('_error')]

    def children(record):
        for child in record.get('related_errors', []):
            yield child
            yield from children(child)

    nested = [child for record in top for child in children(record)]
    return {
        'native_errors': dict(Counter(r['type'] for r in top)),
        'native_error_count': len(top),
        'native_nested_detail_types': dict(Counter(r['type'] for r in nested)),
        'native_nested_detail_count': len(nested),
        'native_warning_types': dict(Counter(r['type'] for r in records if r.get('type', '').endswith('_warning'))),
        'error_count_interpretation': 'native_error_count counts top-level groups; nested details are retained separately and must not be ignored or blindly added as independent groups.',
    }
