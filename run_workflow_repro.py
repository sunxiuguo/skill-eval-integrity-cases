#!/usr/bin/env python3
"""Characterize three known workflow gaps, plus a positive control.

Synthetic input only; not a fix, evaluator, or model-quality benchmark.
Copyright 2026 skill-eval-integrity-cases contributors. Apache-2.0.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / 'vendor' / 'aggregate_benchmark.py'
BLOB = '3e66e8c105be9bab9f0e9c61f0d1482619401580'


def main():
    source = VENDOR.read_bytes()
    actual_blob = hashlib.sha1(b'blob ' + str(len(source)).encode() + b'\0' + source).hexdigest()
    if actual_blob != BLOB:
        raise RuntimeError('Vendor source differs from pinned Git blob')
    rows = []
    cases = [
        ('nested_control', 'eval-0', True, 'without_skill', 2, '+1.00'),
        ('descriptive_nested', 'list-group-members', True, 'without_skill', 0, '+0.00'),
        ('documented_flat', 'eval-0', False, 'without_skill', 0, '+0.00'),
        ('improve_old_baseline', 'eval-0', True, 'old_skill', 2, '-1.00'),
    ]
    with tempfile.TemporaryDirectory(prefix='skill-workflow-') as tmp:
        for name, eval_name, nested, baseline, expected_count, expected_delta in cases:
            folder = Path(tmp) / name
            for config, rate in [('with_skill', 1), (baseline, 0)]:
                run = folder / eval_name / config
                if nested:
                    run /= 'run-1'
                run.mkdir(parents=True)
                grade = {
                    'summary': {'pass_rate': rate, 'passed': rate, 'failed': 1-rate, 'total': 1},
                    'expectations': [{'text': 'Synthetic marker', 'passed': bool(rate),
                                      'evidence': 'Synthetic fixture; no model executed'}],
                }
                (run / 'grading.json').write_text(json.dumps(grade), encoding='utf-8')
            (folder / eval_name / 'eval_metadata.json').write_text(json.dumps({
                'eval_id': 0, 'eval_name': 'list-group-members', 'assertions': []
            }), encoding='utf-8')
            command = [sys.executable, str(VENDOR), str(folder)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=20,
                                    env={'PATH': os.path.dirname(sys.executable),
                                         'LANG': 'C.UTF-8', 'PYTHONNOUSERSITE': '1'})
            if result.returncode != 0:
                raise RuntimeError(f'{name}: exit {result.returncode}: {result.stderr}')
            benchmark = json.loads((folder / 'benchmark.json').read_text(encoding='utf-8'))
            count = len(benchmark['runs'])
            delta = benchmark['run_summary']['delta']['pass_rate']
            if (count, delta) != (expected_count, expected_delta):
                raise RuntimeError(f'{name}: pinned behavior changed: {(count, delta)}')
            rows.append({
                'case': name, 'exit_code': result.returncode,
                'observed_run_count': count, 'pass_rate_delta': delta,
                'expected_complete_run_count': 2, 'expected_candidate_minus_baseline': '+1.00',
                'stdout': result.stdout.replace(tmp, '<synthetic temporary directory>'),
                'stderr': result.stderr.replace(tmp, '<synthetic temporary directory>'),
                'benchmark': benchmark,
                'markdown': (folder / 'benchmark.md').read_text(encoding='utf-8'),
            })
    output = ROOT / 'results'
    output.mkdir(exist_ok=True)
    receipt = {'status': 'PASS: pinned workflow behaviors reproduced, not corrected',
               'source_git_blob': BLOB, 'source_sha256': hashlib.sha256(source).hexdigest(),
               'synthetic_only': True, 'cases': rows}
    (output / 'workflow-observations.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{k: row[k] for k in ('case', 'exit_code', 'observed_run_count', 'pass_rate_delta')}
                      for row in rows], indent=2))


if __name__ == '__main__':
    main()
