"""In-process GLSim consensus: no wallet, signing, RPC, or hosted deployment."""
import json
from pathlib import Path
import pytest
from glsim.engine import SimEngine
from glsim.state import StateStore, TxStatus
from glsim.consensus import run_consensus

URL = 'https://www.iana.org/help/example-domains'
# Paraphrased deterministic fixture based on IANA, reviewed 2026-09-29.
BODY = 'Example domains including example.com are maintained for documentation purposes. They cannot be registered or transferred.'

@pytest.mark.parametrize('scenario,claim,verdict', [
    ('SUPPORTED', 'Example Domain is intended for documentation use.', 'SUPPORTED'),
    ('CONTRADICTED', 'IANA allows example.com to be registered and transferred.', 'CONTRADICTED'),
    ('UNAVAILABLE', 'Example Domain is intended for documentation use.', 'SUPPORTED'),
    ('DISAGREEMENT', 'Example Domain is intended for documentation use.', 'SUPPORTED'),
])
def test_five_validators(scenario, claim, verdict):
    calls = {'web': 0, 'llm': 0}
    def web(req):
        calls['web'] += 1
        return {'ok': {'response': {'status': 503 if scenario == 'UNAVAILABLE' else 200,
                'headers': {'content-type': b'text/plain'},
                'body': (BODY + (' Changed evidence.' if scenario == 'DISAGREEMENT' and calls['web'] > 1 else '')).encode()}}}
    def llm(req):
        calls['llm'] += 1
        return {'ok': json.dumps({'verdict': verdict, 'reason': f'Source classification, observation {calls["llm"]}.'})}
    engine = SimEngine(StateStore(seed='web-claim-attestor-tests'), web_handler=web, llm_handler=llm)
    engine.activate()
    try:
        addr, _ = engine.deploy('contracts/web_claim_attestor.py')
        i = engine.call_method(addr, 'create_attestation', [claim, URL, ''])
        before = engine.call_method(addr, 'get_attestation', [i])
        def execute():
            return engine.call_method(addr, 'resolve_attestation', [i]), b''
        result = run_consensus(engine, execute, num_validators=5, max_rotations=1)
        row = engine.call_method(addr, 'get_attestation', [i])
        assert len(result.votes) == 5
        if scenario == 'DISAGREEMENT':
            assert result.status == TxStatus.UNDETERMINED
            assert result.votes == ['disagree'] * 5
            assert row == before
        else:
            assert result.status == TxStatus.FINALIZED and result.error is None
            assert result.votes == ['agree'] * 5
            assert calls['web'] == 6  # GLSim runs leader plus five checking validators.
            if scenario == 'UNAVAILABLE':
                assert result.result == 'UNAVAILABLE'
                assert row == before and calls['llm'] == 0
            else:
                assert row['status'] == 'ATTESTED' and row['verdict'] == verdict
                assert calls['llm'] == 6
        report = {'scenario':scenario,'mode':'GLSim in-process; deterministic web/LLM mocks',
            'votes':result.votes,'status':result.status.value,'result':result.result,
            'calls':dict(calls),'attestation':row}
        if scenario == 'UNAVAILABLE':
            scenario = 'RETRY'
            retry = run_consensus(engine, execute, num_validators=5, max_rotations=1)
            assert retry.status == TxStatus.FINALIZED and retry.error is None
            assert engine.call_method(addr,'get_attestation',[i])['status'] == 'ATTESTED'
            report['retry'] = 'SUPPORTED; ATTESTED; five agree'
        Path('reports/glsim-'+report['scenario'].lower()+'.json').write_text(json.dumps(report,indent=2))
    finally:
        engine.deactivate()
