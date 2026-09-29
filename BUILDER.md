# Builder submission draft

## Name

Web Claim Attestor

## One-liner

A GenLayer Intelligent Contract that verifies factual claims against authoritative web sources and anchors the reviewed evidence on-chain.

## Description

A factual answer from one model is difficult to trust or audit: the model may hallucinate, the webpage may change, and a later reader may not know which evidence was reviewed. Web Claim Attestor creates a wallet-bound commitment to a factual claim, a public authoritative HTTPS source selected by the creator, and optional context.

During resolution, GenLayer validators independently fetch live web evidence, normalize and bound it, and classify the claim as SUPPORTED, CONTRADICTED, or UNCLEAR. Acceptance requires material agreement on availability, verdict, and the SHA-256 fingerprint of the exact evidence used. A shared verdict based on different evidence cannot satisfy that comparison. Accepted attestations are immutable, while explanatory wording remains non-material.

Unavailable sources remain pending and retryable instead of becoming false negative attestations. With four public methods and explicit provenance, the contract is a reusable primitive for applications that need an auditable link between a submitted claim, its source, and an accepted evidence-based outcome.

## Expected verification outcome

Creating an attestation stores a wallet-bound commitment to the claim and source. Resolving it causes GenLayer validators to fetch the public HTTPS source, agree on the exact evidence fingerprint, and classify the claim as SUPPORTED, CONTRADICTED, or UNCLEAR. If the source is unavailable, no final attestation is persisted and resolution remains retryable.

## Submission status

Draft, not submitted. Live Studio-dev validation succeeded on chain 61997 at `0xa436C779DcF4e8aF5e4454eF76eDB0E2e13F4e08`, with attestation #1 ATTESTED / AVAILABLE / SUPPORTED. See [live validation](reports/STUDIO-DEV-LIVE.md) for exact transactions and provenance. GitHub has not been pushed; a published repository URL is not yet available.
