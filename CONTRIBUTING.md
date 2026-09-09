# Contributing

Project Seed treats evaluation integrity as a first-class invariant.

Before proposing capability changes:

1. add/adjust visible tests without weakening existing assertions;
2. do not place secrets or private holdouts in the repository;
3. do not make candidate-mutated code able to change canonical scoring/security logic;
4. state expected capability gain and cost impact;
5. distinguish benchmark improvement from evidence of recursive amplification.

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

A change that increases visible benchmark performance while reducing hidden/OOD performance, reproducibility or evaluation integrity should not be promoted.
