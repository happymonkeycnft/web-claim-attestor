"""Local source audit and reproducible metrics. Does not load contract/keys/network."""
import ast
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'contracts/web_claim_attestor.py'
source = path.read_text()
tree = ast.parse(source)
contract = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='WebClaimAttestor')
methods = {n.name: [ast.unparse(d) for d in n.decorator_list] for n in contract.body
           if isinstance(n,ast.FunctionDef) and n.decorator_list}
assert methods == {'create_attestation':['gl.public.write'], 'resolve_attestation':['gl.public.write'],
                   'get_attestation':['gl.public.view'], 'get_attestation_count':['gl.public.view']}
resolve = next(n for n in contract.body if isinstance(n,ast.FunctionDef) and n.name=='resolve_attestation')
closures = [n for n in resolve.body if isinstance(n,ast.FunctionDef)]
for closure in closures:
    names = {n.id for n in ast.walk(closure) if isinstance(n,ast.Name)}
    assert not names.intersection({'self','row','memory'})
assert source.count('gl.nondet.exec_prompt(') == 1
assert source.index('gl.storage.copy_to_memory(row)') < source.index('def leader_fn')
assert source.index('accepted = gl.vm.run_nondet') < source.index('row.availability =')
# Execute only the pure prompt formatter to measure actual serialized inputs.
formatter = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_prompt')
ns = {'json':json}
exec(compile(ast.Module(body=[formatter],type_ignores=[]),str(path),'exec'),ns)
f = ns['_prompt']
metrics = {'source_bytes':len(path.read_bytes()), 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'public_methods':len(methods),'prompt_empty_chars':len(f('','','')),
    'prompt_example_chars':len(f('Example Domain is intended for documentation use.','','Example domains are maintained for documentation purposes.')),
    'prompt_max_plain_chars':len(f('x'*500,'x'*1000,'x'*3500)),
    'prompt_hard_cap_chars':6000,
    'closure_storage_audit':'PASS', 'interface_ast':'PASS'}
# High-confidence credential patterns; hashes/addresses intentionally aren't secrets.
patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}',
            r'(?i)(?:private_key|api_key|secret_key)\s*[:=]\s*["\'][A-Za-z0-9+/=_-]{24,}']
for p in root.rglob('*'):
    if not p.is_file() or any(part.startswith('.') or part == '__pycache__' for part in p.relative_to(root).parts):
        continue
    if p.suffix not in ('.py', '.md', '.txt', '.json', '.toml', '.yaml', '.lock'):
        continue
    assert not any(re.search(pattern,p.read_text()) for pattern in patterns), f'secret-like data in {p}'
metrics['secret_scan'] = 'PASS (project text credential-pattern scan)'
(root/'reports/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
