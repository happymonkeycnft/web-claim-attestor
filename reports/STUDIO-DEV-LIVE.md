# Studio-dev live validation

Completed 2026-09-29 on chain **61997**, canonical RPC https://studio-dev.genlayer.com/api. CLI 0.40.0-rc.3; genlayer-js 2.0.0-rc.1. This supersedes the earlier unfunded preflight outcome.

- Deployer: `0x4eD1d43e060e220724EE96E9c177E7548735994d`
- Balance before: 2 GEN (2000000000000000000 wei)
- Contract: `0xa436C779DcF4e8aF5e4454eF76eDB0E2e13F4e08`
- Deployment: `0xbd45b1fb6cbb0c6d3c6ca26397ee6b7f35cf1793c9ae38b866180f799ef00175`
- Creation: `0x4a1014df54439e796d26bd1e9462a2b6cca64b1a6b6f919cba120708447cb87e`
- Resolution: `0x5b7e124d55617063139518eca7cee7e21984d575aaa603acaf7385dc58f87286`
- All three transactions: FINALIZED, accepted, FINISHED_WITH_RETURN.
- Resolve committee: 3 AGREE, 2 IDLE after quorum; no disagreement reported.
- Initial count: 0; final count: 1; attestation ID: 1.
- Final result: ATTESTED / AVAILABLE / SUPPORTED.
- Source commitment: `ae8c570c9a2525cb03bb7985361c25881e80113959eb71c50f0eb1c750d98286`
- Evidence fingerprint: `95f5703a63f18c2da300bb57d4f5c5229d04176d64f608040e597c723e530583`
- Reason (193 characters): The source explicitly states example domains like example.com are 'maintained for documentation purposes' and 'may be used as illustrative examples in documents,' directly supporting the claim.
- Final balance: 1.999762687249997531 GEN (1999762687249997531 wei).

## Fee estimates

| Step | Fresh feeValue (wei) |
| --- | --- |
| Deployment | 100000000000010352 |
| Create | 378507600010352 |
| Resolve | 383955600010352 |

Each balance exceeded its fresh estimate. Full distributions, policies, pre-write balances, nonce checks, and public consensus receipt summaries are recorded in `live-deployment.json`. Machine-specific wallet tooling and raw operational records are excluded from Git. FeeValue is the funded budget, not the final consumed fee.

## Verification

The deployed source was read back and SHA-256 matched the approved local source. Local source remains exactly 9,172 bytes with SHA-256 `e35ec8d171847d3685224a5fccda2e506a1cd3b66ec62dd3d8585e5e3fa6edfc`.

Creator, claim, URL, context and commitment matched the PENDING record after resolution. The commitment was independently recomputed from its length-prefixed inputs. The fingerprint is valid SHA-256 hex and the 193-character reason satisfies its bound. Reads used latest-final state.

Exactly one deployment, one create and one resolve were broadcast, with no broadcast retry. Fee estimation for writes uses the SDK's simulation-backed estimator; these simulations are distinct from the single state-changing broadcasts. No live unavailable case was created; retry/no-inference behavior remains covered by local GLSim.

No explorer contract URL is claimed: the installed Studio-dev preset intentionally exposes no block explorer, and the suggested explorer host could not be verified through the web tool. The RPC readback is the verification record.

No contract logic changes, faucet, GitHub push or Builder submission occurred. Ready for the next authorized GitHub push and Builder submission preparation. A published repository URL remains to be supplied after an authorized push.
