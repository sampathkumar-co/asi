# Gate 1 Local Evaluator Manifest

The local calibration answer key is intentionally stored outside the candidate-readable repository.

- Suite: `gate1-local-calibration-v1`
- External evaluator key filename: `gate1_local_answers_v1.json`
- SHA-256: `af9cbd0ff38488ffc2fbb607e6343d478cc77d5c81cf2721f70f4d4ccaa98b6f`
- Canonical control-plane location for the current Sampath Windows run: `%LOCALAPPDATA%\\ProjectSeedPrivate\\gate1_local_answers_v1.json`

The repository contains the task suite and scoring implementation, but not the accepted answers. Evidence reports must record this SHA-256 before their scores are interpreted.

This calibration suite is not a final hidden/OOD Gate-1 certification suite; it is used to establish that the local model has sufficient headroom and that the Raw-vs-Seed measurement path is functioning correctly.
