#!/usr/bin/env python3
"""Synthetic black-box probes of the unmodified, pinned upstream aggregator.
Not an evaluator, security boundary, or model-quality benchmark.
"""
import collections, copy, hashlib, json, os, pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
source=(ROOT/'vendor'/'aggregate_benchmark.py').read_bytes()
assert hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest() == '3e66e8c105be9bab9f0e9c61f0d1482619401580', 'Vendor source differs from pinned Git blob'
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2)+'\n')
def grading(rate):
    return {'summary':{'pass_rate':rate,'passed':int(rate),'failed':1-int(rate),'total':1},'expectations':[{'text':'Synthetic expected marker exists','passed':bool(rate),'evidence':'Synthetic fixture control; no model executed'}],'execution_metrics':{'total_tool_calls':1,'output_chars':900,'errors_encountered':0}}
def setup(name):
    folder=OUT/name
    if folder.exists(): shutil.rmtree(folder)
    for config,rates in [('with_skill',[1,0,1]),('without_skill',[1,1,1])]:
        for n,rate in enumerate(rates,1):
            d=folder/'eval-0'/config/f'run-{n}'
            write(d/'grading.json',grading(rate)); write(d/'timing.json',{'total_duration_seconds':2,'total_tokens':100})
    write(folder/'planned-runs.json',{'note':'Test-oracle manifest, NOT a supported upstream input. Defines intended fixture completeness.','planned':[{ 'eval_id':0,'configuration':c,'run_number':n} for c in ['with_skill','without_skill'] for n in range(1,4)]})
    return folder
names=['complete_control','missing_grading','invalid_schema','blocked_baseline','unbalanced_pairs','missing_tokens','timing_present_tokens_ignored']
reports=[]
for name in names:
    p=setup(name); w=p/'eval-0'/'with_skill'; b=p/'eval-0'/'without_skill'
    expected='valid complete measurement: candidate 2/3, baseline 3/3, delta -1/3; 100 tokens each'
    if name=='missing_grading':
        (w/'run-2'/'grading.json').unlink(); expected='incomplete candidate: missing grading must not be treated as evidence of improvement'
    elif name=='invalid_schema':
        write(b/'run-1'/'grading.json',{}); expected='invalid grading schema; do not convert missing grade to numeric 0'
    elif name=='blocked_baseline':
        g=grading(1); g['expectations'][0]['evidence']='Execution blocked: shell tool unavailable; criterion not executed.'; g['execution_metrics']['total_tool_calls']=0
        g['user_notes_summary']={'uncertainties':['Execution blocked; graded on documented intent only.']}
        write(b/'run-1'/'grading.json',g); expected='semantic honesty control: unexecuted case cannot support a pass; aggregator may lack a typed execution-status contract'
    elif name=='unbalanced_pairs':
        shutil.rmtree(b/'run-2'); shutil.rmtree(b/'run-3'); expected='candidate has 3 runs, baseline 1; report observed counts accurately and identify unpaired comparison'
    elif name=='missing_tokens':
        for d in w.glob('run-*'): write(d/'timing.json',{'total_duration_seconds':2})
        expected='candidate tokens unknown; output_chars=900 is not a measured token count'
    elif name=='timing_present_tokens_ignored':
        for d in w.glob('run-*'):
            g=json.loads((d/'grading.json').read_text()); g['timing']={'total_duration_seconds':2}; write(d/'grading.json',g)
        expected='measured sibling tokens=100 must remain visible when grading already has duration=2'
    cmd=[sys.executable,'vendor/aggregate_benchmark.py',str(p.relative_to(ROOT)),'--skill-name','synthetic-integrity-probe']
    run=subprocess.run(cmd,cwd=ROOT,env={'PATH':os.path.dirname(sys.executable),'LANG':'C.UTF-8','PYTHONNOUSERSITE':'1'},capture_output=True,text=True,timeout=20)
    (p/'stdout.txt').write_text(run.stdout); (p/'stderr.txt').write_text(run.stderr)
    bench=json.loads((p/'benchmark.json').read_text()) if (p/'benchmark.json').exists() else None
    report={'case':name,'command':['python3',*cmd[1:]],'command_note':'python3 denotes the interpreter executing this harness','exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'expected_test_oracle':expected,'actual':{'observed_counts':dict(collections.Counter(r['configuration'] for r in bench['runs'])),'reported_runs_per_configuration':bench['metadata']['runs_per_configuration'],'run_summary':bench['run_summary']} if bench else None}
    write(p/'observation.json',report); reports.append(report)
write(OUT/'observations.json',reports)
# Assertions describe the pinned implementation, not desired product semantics.
r={x['case']:x for x in reports}
assert all(x['exit_code']==0 for x in reports)
assert r['complete_control']['actual']['run_summary']['delta']['pass_rate']=='-0.33'
assert r['complete_control']['actual']['run_summary']['delta']['tokens']=='+0'
assert r['missing_grading']['actual']['run_summary']['delta']['pass_rate']=='+0.00'
assert r['missing_grading']['actual']['observed_counts']['with_skill']==2
assert r['invalid_schema']['actual']['run_summary']['without_skill']['pass_rate']['mean']==0.6667
assert r['blocked_baseline']['actual']['run_summary']['without_skill']['pass_rate']['mean']==1.0
assert r['unbalanced_pairs']['actual']['observed_counts']['without_skill']==1
assert r['unbalanced_pairs']['actual']['reported_runs_per_configuration']==3
assert r['missing_tokens']['actual']['run_summary']['with_skill']['tokens']['mean']==900.0
assert r['missing_tokens']['actual']['run_summary']['delta']['tokens']=='+800'
assert r['timing_present_tokens_ignored']['actual']['run_summary']['with_skill']['tokens']['mean']==900.0
assert r['timing_present_tokens_ignored']['actual']['run_summary']['delta']['tokens']=='+800'
assert 'Warning' in r['missing_grading']['stdout'] or 'Warning' in r['missing_grading']['stderr']
assert '3 runs each per configuration' in (OUT/'unbalanced_pairs'/'benchmark.md').read_text()
assert '900' in (OUT/'missing_tokens'/'benchmark.md').read_text()
write(OUT/'reproduction-check.json',{'status':'PASS: all seven observed behaviors reproduced','python':sys.version,'source_sha256':hashlib.sha256((ROOT/'vendor'/'aggregate_benchmark.py').read_bytes()).hexdigest(),'cross_tool_comparison':'not run; agent-skill-eval is not installed','network':'upstream script and probe use no network APIs; OS network isolation not independently verified'})
print(json.dumps([{'case':x['case'],'exit':x['exit_code'],'counts':x['actual']['observed_counts'],'delta':x['actual']['run_summary']['delta']} for x in reports],indent=2))
