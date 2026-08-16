# poc-revenue

> **Cubiczan stack** — [CHP](https://github.com/Cubiczan/consensus-hardening-protocol) · [control-spine](https://github.com/Cubiczan/control-spine) · **You are here:** `poc-revenue`

**ASC 606 over-time / percentage-of-completion.** Cost-to-cost POC, constrained transaction price, contract asset vs liability, full estimated loss on an onerous contract. Koil Energy's filing carries revenue-recognition and POC language. There was no repo. Now there is.

Identify the performance obligation first. This engine measures it. It does not decide over-time vs point-in-time.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What it produces

| Artefact | What a tester samples |
|---|---|
| Contract register | TP, constrained price, estimated costs, costs incurred, billings |
| POC computation | costs incurred / estimated total cost, quantized to 4 decimals |
| Balance sheet split | contract asset (unbilled) vs contract liability (billings in excess) |
| Onerous-contract provision | remaining loss so cumulative GP equals the full estimated loss |

A $1,000,000 contract, $800,000 estimated cost, $200,000 incurred, $300,000 billed: POC **25%**, revenue **250,000**, liability **50,000**. A $1,200,000 cost estimate on the same price: estimated loss **200,000**, provision **150,000**. Both are in the tests.

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
poc-revenue examples/contracts.json --period "H1 2026" --owner "Controller"
```

## Compliance spine

Vendored `control-spine`. Over-time vs point-in-time is an input in the foundation. The engine measures; it does not identify performance obligations. Unsigned packs are `EXPLORING`. A named owner on a non-empty population reaches `LOCKED`.
