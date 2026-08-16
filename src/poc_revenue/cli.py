from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from control_spine import exit_code
from poc_revenue.engine import Contract, Timing, measure
from poc_revenue.evidence import evidence_markdown, evidence_pack


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="ASC 606 / POC measurement + evidence pack")
    p.add_argument("contracts_json")
    p.add_argument("--period", default="current")
    p.add_argument("--owner", default="")
    args = p.parse_args(argv)
    raw = json.loads(Path(args.contracts_json).read_text())
    rows = []
    for item in raw["contracts"]:
        c = Contract(
            contract_id=item["contract_id"],
            description=item.get("description", ""),
            timing=Timing(item.get("timing", "over_time")),
            transaction_price=item["transaction_price"],
            constrained_price=item["constrained_price"],
            estimated_total_cost=item["estimated_total_cost"],
            costs_incurred_to_date=item["costs_incurred_to_date"],
            billings_to_date=item["billings_to_date"],
            complete=item.get("complete", False),
        )
        rows.append(measure(c))
    pack = evidence_pack(tuple(rows), args.period, args.owner)
    print(evidence_markdown(pack))
    print(pack["lock_state"], file=sys.stderr)
    return exit_code(pack)


if __name__ == "__main__":
    raise SystemExit(main())
