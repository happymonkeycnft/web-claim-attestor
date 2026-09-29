# Web Claim Attestor

## What it does

A GenLayer Intelligent Contract that verifies a factual claim against a public authoritative webpage and persists a consensus-backed attestation. Validators independently retrieve the source and must agree on availability, verdict, and the exact bounded evidence fingerprint. Anyone may resolve a pending record; only creation binds the submitting wallet.

## Trust problem

One model may hallucinate, external sources change, and a prose answer provides weak provenance. This contract anchors the creator's inputs and the evidence reviewed during accepted validator consensus. Different evidence cannot pass the contract's material comparison merely because models produce the same verdict.

## Result semantics

| Outcome | Meaning | State |
| --- | --- | --- |
| SUPPORTED | Evidence clearly supports the claim | ATTESTED |
| CONTRADICTED | Evidence materially contradicts the claim | ATTESTED |
| UNCLEAR | Retrieved evidence is insufficient or ambiguous | ATTESTED |
| UNAVAILABLE | Source could not be reliably retrieved | PENDING; retry allowed |

UNAVAILABLE is retryable and is never converted into CONTRADICTED. Non-200 responses, unsupported content types, empty/oversized bodies, decoding failures, and recognized challenge pages avoid inference. A successful unavailable execution returns UNAVAILABLE but leaves every stored field unchanged. Inference/schema errors or failed consensus also cannot finalize a record. ATTESTED records cannot be resolved again.

## Evidence provenance

`source_commitment` is SHA-256 over a versioned, length-prefixed serialization of ID, lowercase creator address, exact claim, normalized URL, and exact context. Each UTF-8 field has a four-byte unsigned big-endian byte length. The initial domain-separation field is `web-claim-attestor:v1`; the ID is decimal text. Claim/context whitespace is preserved; URL normalization lowercases scheme/host, removes port 443 and fragment, and supplies `/` for an empty path.

This proves the wallet committed to those inputs in this contract. It does not prove domain ownership, webpage authorship, legal identity, or source immutability. It is not a cross-chain replay-proof signature.

`evidence_fingerprint` is SHA-256 of the UTF-8 encoding of the exact normalized, bounded evidence passed to the model. HTML scripts, styles, navigation, headers, footers, templates and noscript text are excluded; whitespace is collapsed. Evidence is limited to 3,500 characters, with additional deterministic trimming when JSON escaping would push the complete prompt above 6,000 characters. Reason wording is bounded to 240 characters and is non-material; the leader's reason is stored after material agreement.

## Methods

| Method | Type | Behavior |
| --- | --- | --- |
| `create_attestation(claim, source_url, context)` | write → integer ID | Create PENDING record; use `""` for optional context |
| `resolve_attestation(attestation_id)` | write → string | Return verdict and finalize, or return UNAVAILABLE unchanged |
| `get_attestation(attestation_id)` | view → dictionary | Return inputs, ID, creator, commitments and result fields |
| `get_attestation_count()` | view → integer | Return number created |

Claim ≤500 characters; URL ≤500; context ≤1,000. Claims must be nonblank. Unusual C0 input controls are rejected. URLs must have a public-looking ASCII DNS hostname and use HTTPS on the default port. Credentials, IP literals, local suffixes, malformed labels, whitespace/control characters, and malformed percent escapes are rejected. DNS authority is selected by the creator, not certified by the contract.

## Testing

Python 3.12 is required. The exact tested tooling is pinned in `requirements.txt` and its full resolved environment in `requirements.lock`: genlayer-test 0.30.0rc2, genlayer-py 0.19.0rc2, genvm-linter 0.11.1rc2, cloudpickle 3.1.2. GenVM manager bundle: v0.6.0-rc6. The contract header pins its py-genlayer runner.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock
export GENVM_VERSION=v0.6.0-rc6
.venv/bin/pytest tests/direct tests/integration -q -W error::RuntimeWarning
.venv/bin/genvm-lint check contracts/web_claim_attestor.py
.venv/bin/genvm-lint schema contracts/web_claim_attestor.py --json
.venv/bin/python -m compileall -q contracts tests tools
.venv/bin/python tools/audit.py
git diff --check
```

69 direct cases and four in-process GLSim scenarios pass. SUPPORTED and CONTRADICTED use deterministic fixtures paraphrased from [IANA's example-domain policy](https://www.iana.org/help/example-domains). UNAVAILABLE injects an HTTP 503 and verifies unchanged PENDING state, zero inference, and successful retry. A fourth scenario changes validator evidence and verifies disagreement and storage rollback. GLSim executes one leader and five checking validators per scenario. Mocked responses exercise the real SDK decode path and GLSim consensus engine; no transactions are signed.

The RC suite's flat web mocks discard headers and its LLM convenience mocks decode JSON prematurely for this runner. Tests therefore use the supported full web response shape and injected local handlers returning the actual SDK wire shape. No dependency code is patched. Closure pickling is tested with runtime warnings treated as failures.

Public reports are in `reports/`; machine-specific wallet scripts and raw operational receipts are excluded from Git. Generated contract artifacts are kept separately because gltest clears its artifact directory. See `VALIDATION.md` for the final local validation record and `BUILDER.md` for submission drafts.

## Network target

The validated hosted target is **Studio-dev, chain 61997**, canonical RPC `https://studio-dev.genlayer.com/api`, using the RC `studio_devnet` definition. Local simulations use 61127. One hosted deployment and one create/resolve demo have finalized successfully. No faucet, GitHub push, frontend, or Builder submission was performed.

The [official v0.6 migration guide](https://docs.genlayer.com/developers/consensus-v06-migration) specifies the Python v0.19 RC / Studio v0.123 RC family. Before an authorized hosted run, inspect the chain identity and current fee policy, measure/quote fees where required, and verify finalization plus execution success. Local GLSim does not establish hosted compatibility or provide a production fee profile.

## Limitations

- The source may change later. An attestation reflects the evidence retrieved during accepted validator consensus, not future page contents or universal truth.
- Creator commitment does not prove domain ownership or authority. The user selects the authoritative source; there is no domain allowlist.
- Sources must be public HTTPS. The contract validates URL syntax but cannot inspect DNS resolution, redirect destinations, or enforce network egress policy; those remain GenLayer web-runtime responsibilities.
- Raw GET supports UTF-8 HTML/plain text. JavaScript-only pages, login walls, PDFs, other encodings, missing content types, and bodies over 128 KiB may remain retryable. The SDK exposes no streaming download cap; the body-size check occurs after retrieval.
- The first bounded text may omit relevant passages. Dynamic content can cause fingerprint disagreement. HTML cleanup and challenge detection are conservative heuristics and may exclude valid material or miss unusual error pages.
- Prompt instructions and consensus reduce risk but do not eliminate prompt injection or correlated model mistakes. Reason prose is not independently agreed factual evidence.
- Hashes commit to evidence but do not archive it; independent later reconstruction requires retaining the corresponding source text. No timestamp field is invented: PENDING/ATTESTED represent created/finalized state, with transaction metadata supplied by the chain after deployment.
- Local web and LLM fixtures are deterministic. One live Studio-dev SUPPORTED case has now finalized successfully; it is not a broad accuracy benchmark. Other live verdicts and unavailable sources were not exercised.

## Live Studio-dev demo

Contract `0xa436C779DcF4e8aF5e4454eF76eDB0E2e13F4e08` on chain **61997**. Attestation **#1** finalized as **ATTESTED / AVAILABLE / SUPPORTED**; final count is 1.

- Deployment transaction: `0xbd45b1fb6cbb0c6d3c6ca26397ee6b7f35cf1793c9ae38b866180f799ef00175`
- Resolve transaction: `0x5b7e124d55617063139518eca7cee7e21984d575aaa603acaf7385dc58f87286`
- Source commitment: `ae8c570c9a2525cb03bb7985361c25881e80113959eb71c50f0eb1c750d98286`
- Evidence fingerprint: `95f5703a63f18c2da300bb57d4f5c5229d04176d64f608040e597c723e530583`

The deployed source matches the approved SHA-256. See [live validation](reports/STUDIO-DEV-LIVE.md) for fee estimates, creation transaction, consensus, readback and limitations. Explorer contract URL is unverified; no stable-chain explorer is substituted.
