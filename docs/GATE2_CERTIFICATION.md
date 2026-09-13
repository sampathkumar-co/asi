# Gate 2 Certification Plan

Updated: 2026-09-13

## Status

Gate 2 is **not empirically certified** after three preregistered private/OOD attempts. Private v1 failed verifier acceptance; private v2 failed transfer; private v3.1 narrowly failed the frozen mean-gain criterion. All three are permanently retired as fresh certification evidence.

## Private holdout v1 outcome

Frozen source commit: `ec1e98315a0baa2fe47d344702790b86bbc6132f`.

Preregistration commit: `2126f64b7d37964edf019794507cd19d021f2fd8`.

Observed on 18 valid pairs: Raw mean **0.70556**, Seed mean **0.94167**, mean gain **+0.23611**, strict Seed wins **66.67%**, paired-bootstrap CI **[+0.11944, +0.37222]**, Seed dual-verifier acceptance **50%**.

The valid-pair, Seed-mean, mean-gain, strict-win, and CI requirements passed. Verifier acceptance failed. Under the frozen all-checks rule, **promotion_pass=false** and Gate 2 remains uncertified.

Private v1 is permanently retired for future certification. See [`GATE2_PRIVATE_HOLDOUT_V1_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V1_RESULT.md).

Private-v2 result: Raw **0.81250**, Seed **0.82083**, gain **+0.00833**, strict wins **33.33%**, CI **[-0.07361, +0.09583]**, verifier acceptance **88.89%**, 18 valid pairs. `promotion_pass=false`. The current v3.1 public-development result is Raw **0.76875**, Seed **0.98750**, gain **+0.21875**, strict wins **75%**, CI **[+0.06250, +0.46875]**, acceptance **100%**; it is explicitly non-certifying. See [`GATE2_PRIVATE_HOLDOUT_V2_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V2_RESULT.md) and [`GATE2_V31_PUBLIC_RESULT.md`](GATE2_V31_PUBLIC_RESULT.md).

## Private v3.1 holdout outcome

Candidate freeze commit `2b98491641426f9ebe1678b8491a18a583e6c784` passed GitHub Actions CI #155. Preregistration commit `393c22abf67e70675870f7f054eed023685cc08b` passed CI #156 before inference. The external suite `gate2-private-holdout-v31` contained 18 balanced tasks and passed the preregistered pre-inference structure, overlap, and identifiability audits.

Frozen external hashes: task `408542488bc207f2d7b3f169ca4357e001e3cfded8872249ac17461bdf44f24a`, answer key `d7e104467cc80a472d60ba2a3de32c50c224d5c7d1f0c6a7918c1d3433d364f9`, audit file `431bc0e63e35a45d9a1db41cbe408cd256959ab54e9fcdb7f09552ed94ce0a14`. Official frozen score: Raw **0.78750**, Seed **0.93472**, gain **+0.14722**, strict wins **77.78%**, CI **[+0.01806, +0.28472]**, verifier acceptance **83.33%**. Mean gain alone failed the frozen **>=0.15** requirement. V31P01 Raw also suffered a confirmed CUDA/Ollama startup crash that artificially increased the official Seed-minus-Raw gain; excluding that pair diagnostically yields only **+0.09706** gain. Therefore the infrastructure incident does not create any path to promotion. Full records: [`GATE2_PRIVATE_HOLDOUT_V31_PREREGISTRATION.md`](GATE2_PRIVATE_HOLDOUT_V31_PREREGISTRATION.md) and [`GATE2_PRIVATE_HOLDOUT_V31_RESULT.md`](GATE2_PRIVATE_HOLDOUT_V31_RESULT.md).
## Frozen promotion rule

A Gate-2 certification attempt passes only if all of the following are true:

- valid paired tasks >= **16**;
- Seed mean >= **0.75**;
- mean Seed-minus-Raw gain >= **0.15**;
- strict Seed win rate >= **60%**;
- deterministic paired-bootstrap lower confidence bound > **0**;
- Seed independent+adversarial acceptance >= **75%**;
- Raw and Seed use the same model artifact and resource envelope;
- all campaign, pair, checkpoint, implementation, model, and answer-key integrity checks pass;
- no candidate prompt contains the private answer key or unrevealed observation.

The paired bootstrap is fixed at 4,000 samples with random seed 0.

## Freeze-before-holdout sequence

1. commit the Gate-2 candidate, public calibration record, tests, and protocol documentation;
2. push the candidate commit and require clean GitHub Actions CI;
3. record the frozen candidate commit, implementation digest, model digest, resource envelope, scorer/rubric, and thresholds;
4. create the private/OOD task file and answer key **outside the repository**;
5. independently audit every private task/key pair before inference;
6. record only cryptographic hashes and non-secret metadata in the preregistration;
7. commit and push the preregistration and require clean CI;
8. only then run Raw and Seed inference on the private tasks.
## Holdout requirements

The private suite must contain at least 16 paired research tasks and must not reuse the eight public calibration tasks as certification data. It should cover multiple scientific failure modes rather than one template family.

The private answer key must remain external to GitHub and external to candidate prompts. Task and key files must have independent SHA-256 hashes recorded before inference.

The candidate implementation, model artifact, resource envelope, scoring weights, acceptance rule, bootstrap procedure, and promotion thresholds become immutable once private inference starts.

## Evidence handling

The campaign must checkpoint atomically after each sealed pair. Resume is allowed only when suite, model, model manifest, implementation manifest, settings, task-file hash, and previously sealed pair hashes match exactly.

Malformed output, invalid IDs, repeated experiments, verifier disagreement, resource overspend, or integrity mismatch fail closed according to the frozen protocol. Bounded repair remains permitted only because it is already part of the frozen candidate and consumes the shared envelope.

For future post-v31 campaigns, provider/transport failures and trusted-runner failures are distinct execution incidents rather than model failures. Any such incident makes `clean_execution=false` and therefore makes the campaign non-promotable. Model/protocol output failures and budget exhaustion remain arm-level fail-closed outcomes. Trusted mechanical-support defects are outside the model-repair path and cannot be repaired away.

Raw evidence and private task/key contents remain external. GitHub may contain sanitized score artifacts, hashes, preregistration metadata, and the final audit report.

## No post-inference tuning

After the first private candidate call, do not change the candidate, scorer, thresholds, task file, answer key, or verifier policy based on holdout outcomes. A failed campaign remains failed evidence.

If an evaluator implementation bug is discovered after inference, stop the certification claim, preserve all sealed artifacts, document the incident, and resolve it transparently. Do not silently alter sealed research evidence.

## Interpretation

Passing Gate 2 would show that the frozen Seed scientific-method scaffold improves a fixed model on a preregistered hidden/OOD research benchmark under normalized resources. It would **not** by itself establish AGI, ASI, autonomous recursive self-improvement, or sustained recursive amplification.
