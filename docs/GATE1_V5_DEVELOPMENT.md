# Gate 1 v5 Candidate Development

Updated: 2026-09-10

Status: **FROZEN DEVELOPMENT CANDIDATE — NEW HOLDOUT REQUIRED**

## Why v5 exists

Holdout v4 reproduced a large positive scaffold effect but did not satisfy the frozen broad-reliability rule. Raw scored 3/16 (18.75%) and Seed scored 11/16 (68.75%), a +50 percentage-point gain with a 95% paired-bootstrap CI of [+25 pp, +75 pp]. Strict Seed wins were 8/16 (50%), below the required >=60%.

W401-W416 are therefore retired development evidence. They may be used to diagnose generic failure classes, but never again as fresh certification data.

## Frozen v5 candidate

- Source commit: `c34e1cd31c61efebc513f289ba9ac11cdd4412d0`
- Seed implementation digest: `011881547d85a31cccc3bd66a174e7ae9b3e8506014a6c918d248e78708e286c`
- Attested implementation files: 27
- Local regression: **140/140 PASS** with `ResourceWarning` promoted to error
- Deterministic Gate-1 qualification: **10/10 PASS**
- Qualification content hash: `357b3beac3bbcfb04ccf09b6e00a74dd7fdd95b2ef9ae72f7dd15fc9cff16799`
## Generic reliability changes

v5 targets the generic failure modes observed after v4 without embedding any private answer text into the candidate:

- broaden semantic shortest-path routing to include wording such as `cheapest directed route`;
- broaden project-scheduling routing for `critical-path`, `minimum-time`, `unlimited workers`, and duration/dependency phrasing;
- hide generic `python_compute` when a specialized exact verifier is available, reducing schema pressure and fragile hand-written solvers;
- normalize compact duration labels such as `J6` to task `J` with duration `6`, including mixed suffixed-weight/bare-predecessor payloads;
- prefer exact `python_trace` for supplied Python source instead of reconstructing partial programs;
- canonicalize whitespace-only item separators to no separator for single-character optimization item IDs.

## Retired-v4 development probes

After v4 was sealed and scored, the five both-wrong cases were rerun only as development diagnostics under v5:

- W401: exact shortest-path tool returned the verified unique cheapest route in one Seed step;
- W403: exact DAG tool returned the verified project completion time and critical path in one Seed step;
- W404: mixed compact-duration normalization returned bare task IDs and the verified critical path in one Seed step;
- W412: exact supplied Python source was executed by `python_trace` and verified in one Seed step;
- W413: exact subset optimization returned the unique optimum with canonical single-letter formatting in one Seed step.
These probes confirm closure of the targeted failure classes on retired data. They do **not** change the official v4 score and do **not** certify Gate 1.

## Next promotion attempt

The next valid promotion evidence must come from a new private holdout v5 created only after the v5 candidate was frozen. Before any inference:

1. generate materially new task instances;
2. independently audit correctness, uniqueness and optimality;
3. standardize the answer-key container to the repository scorer schema;
4. preregister task/key hashes, candidate/model identities, resource envelope and unchanged thresholds;
5. run every Raw/Seed pair without architecture changes;
6. score once and publish the result whether it passes or fails.

Gate 1 remains active until one preregistered campaign satisfies every frozen promotion criterion.
