# Local validation record

Validated 2026-09-29. Logs and JSON records are in `reports/`.

### Architecture

Standalone Python Intelligent Contract; deterministic creation and hashing, independent nondeterministic retrieval/adjudication, material consensus, then final storage writes. No existing GenLayer project was modified.

### Public interface

Exactly four ABI methods: create_attestation(claim, source_url, context), resolve_attestation(attestation_id), get_attestation(attestation_id), get_attestation_count(). Two writes and two views; verified by GenVM SDK schema.

### Storage model

TreeMap keyed by sequential u256 ID plus count. Each row holds creator, claim, source_url, context, source_commitment, status, availability, verdict, evidence_fingerprint, reason. PENDING/ATTESTED supplies created/finalized state without redundant booleans or fabricated timestamps.

### Source commitment design

SHA-256 of version tag, decimal ID, lowercase wallet, exact claim, normalized URL and exact context. Each UTF-8 field has a four-byte big-endian byte-length prefix. Binds creator inputs; does not establish ownership, identity, authorship or an immutable webpage.

### Evidence fingerprint design

SHA-256 of exact bounded UTF-8 evidence passed to the structured model call, after HTML cleanup, whitespace normalization, the 3,500-character limit and any additional prompt-cap trimming.

### Availability semantics

Unavailable retrieval returns UNAVAILABLE without changing the row; no final verdict or fingerprint is persisted. Recognized fetch failures invoke zero LLM calls. Retry remains allowed. Model errors and rejected consensus also leave PENDING state intact.

### Verdict semantics

SUPPORTED requires explicit support; CONTRADICTED requires material contradiction; UNCLEAR is a valid final verdict for insufficient/ambiguous retrieved evidence. UNAVAILABLE is never a factual verdict.

### Prompt-injection defenses

The prompt makes the claim task input, treats webpage text as untrusted evidence, forbids following page instructions or changing task/schema, and forbids unevidenced inference. Inputs are JSON-delimited; output keys/types/verdict/reason bounds are validated. These measures are mitigations, not a proof of injection immunity.

### Consensus material fields

availability, verdict, evidence_fingerprint. Both results must pass shape validation. Reason prose is non-material and the accepted leader explanation is stored. One structured inference call per available validator observation; none for known unavailable retrieval.

### Direct tests

69 PASS. Creation/bounds/URL checks, independent commitment reference and mutations, all verdicts, immutability, unavailable/retry/no-inference behavior, malformed model results, validator failures, material agreement, HTML normalization, escaping bounds, injection prompt structure and actual closure serialization. Runtime serialization warnings are treated as test failures.

### GLSim SUPPORTED

PASS. Requested Example Domain documentation-use claim, IANA URL, deterministic policy fixture and structured LLM fixture. Five checking validators agree; one leader plus five validators each fetch and infer once. Not live-model validation.

### GLSim CONTRADICTED

PASS. False claim: IANA allows example.com to be registered and transferred. IANA-derived policy fixture contradicts it; five validators agree on verdict and fingerprint. Not live-model validation.

### GLSim UNAVAILABLE

PASS. Controlled HTTP 503: five agree, six retrieval attempts, zero LLM calls, row unchanged and PENDING. Retrying with available fixture yields SUPPORTED/ATTESTED. Additional GLSim disagreement scenario changes validator evidence: all five disagree, no consensus, complete storage rollback verified.

### GenVM lint

PASS: three AST safety checks on the final source. genvm-linter 0.11.1rc2.

### Semantic/interface validation

PASS: GenVM SDK semantic validation and extracted ABI report exactly four public methods (two write/two view). Python 3.12 compilation, project text credential-pattern scan, git diff --check and whitespace checking every new file also pass.

### Closure/storage safety

PASS: storage row copied to memory before closure creation; only plain URL/claim/context strings captured. Neither closure reads self/row/memory. Validator exceptions vote false. Writes occur after validated consensus; unavailable branch exits before writes. Cloudpickle serialization passes. GLSim independently verifies rollback on material disagreement.

### Source bytes

9172

### Source SHA-256

e35ec8d171847d3685224a5fccda2e506a1cd3b66ec62dd3d8585e5e3fa6edfc

### Prompt size

Example: 790 characters. Ordinary maximum-length inputs/evidence: 5683. Hard cap: 6,000 characters including JSON escaping; evidence is shortened deterministically before hashing when needed.

### README status

Complete: purpose, trust problem, semantics, methods, provenance, reproducible tooling/tests, network target and limitations. See README.md.

### Builder one-liner

A GenLayer Intelligent Contract that verifies factual claims against authoritative web sources and anchors the reviewed evidence on-chain.

### Builder description

A factual answer from one model is difficult to trust or audit: the model may hallucinate, the webpage may change, and a later reader may not know which evidence was reviewed. Web Claim Attestor creates a wallet-bound commitment to a factual claim, a public authoritative HTTPS source selected by the creator, and optional context.

During resolution, GenLayer validators independently fetch live web evidence, normalize and bound it, and classify the claim as SUPPORTED, CONTRADICTED, or UNCLEAR. Acceptance requires material agreement on availability, verdict, and the SHA-256 fingerprint of the exact evidence used. A shared verdict based on different evidence cannot satisfy that comparison. Accepted attestations are immutable, while explanatory wording remains non-material.

Unavailable sources remain pending and retryable instead of becoming false negative attestations. With four public methods and explicit provenance, the contract is a reusable primitive for applications that need an auditable link between a submitted claim, its source, and an accepted evidence-based outcome.

### Expected verification outcome

Creating an attestation stores a wallet-bound commitment to the claim and source. Resolving it causes GenLayer validators to fetch the public HTTPS source, agree on the exact evidence fingerprint, and classify the claim as SUPPORTED, CONTRADICTED, or UNCLEAR. If the source is unavailable, no final attestation is persisted and resolution remains retryable.

Length: 357 characters.

### Remaining limitations

Local GLSim runs deterministic web/model fixtures in-process; no hosted WASM execution or live multi-provider inference has been tested. Source selection/authority, DNS/redirect egress safety, dynamic pages, conservative text extraction, prompt injection and correlated model error remain limitations. Hashes do not archive the page. Hosted fee estimates and finalization must be checked during the later authorized Studio-dev run. See README.md for details.

### Ready for Studio-dev deployment: YES / NO

YES for the next authorized deployment-validation step: all requested local gates pass. This does not claim an already successful hosted deployment or production readiness. Target: Studio-dev 61997, https://studio-dev.genlayer.com/api, genlayer-py 0.19.0rc2 and genlayer-test 0.30.0rc2. GenVM manager bundle v0.6.0-rc6; contract runner pinned in source. No deployment, faucet, signing, GitHub push, frontend or Builder submission performed.
