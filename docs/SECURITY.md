# Security and Control Model

Project Seed studies self-improving agent architectures, so control mechanisms are part of the research design rather than optional deployment polish.

## Gate-4 default restrictions

A candidate descendant:

- cannot mutate evaluator code;
- cannot mutate the self-modification policy;
- cannot mutate provider/credential plumbing;
- cannot mutate CI configuration;
- cannot mutate the running parent in place;
- is evaluated with network access disabled in the provided Docker runner;
- receives CPU, memory and process limits;
- must satisfy explicit promotion evidence.

## Credentials

Credentials never belong in candidate-readable source control. `.env` files are ignored. Real provider keys should be supplied only to a trusted broker/control-plane process with scoped permissions and budget enforcement.

## Hidden evaluations

Hidden cases should be stored outside the repository and not mounted into candidate workspaces. Only trusted evaluator code should see expected answers/scorers.

## Promotion

At Gate 4, promotion is intentionally human-approved. The code can compute a promotion recommendation, but it does not autonomously replace the canonical branch or deploy a descendant.

## Future hardening

- microVM/VM sandboxing;
- signed evaluation receipts;
- separate identities for proposer/evaluator/promoter;
- network egress allowlists and transparent proxy logging;
- immutable artifact store;
- reproducible build hashes;
- resource accounting from external infrastructure rather than self-report;
- canary evals for reward hacking and evaluator tampering;
- multi-model independent verification.
