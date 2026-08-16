"""ASC 606 over-time / cost-to-cost percentage of completion.

Measures a performance obligation that transfers over time using cost-to-cost,
constrains variable consideration to the amount the owner says is probable not
to reverse, and accrues the full estimated loss on an onerous contract.

Point-in-time obligations are out of scope. Identify the performance
obligation first; this engine measures it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


CENTS = Decimal("0.01")


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


class Timing(str, Enum):
    OVER_TIME = "over_time"
    POINT_IN_TIME = "point_in_time"


@dataclass(frozen=True)
class Contract:
    contract_id: str
    description: str
    timing: Timing
    transaction_price: Decimal
    constrained_price: Decimal
    estimated_total_cost: Decimal
    costs_incurred_to_date: Decimal
    billings_to_date: Decimal
    complete: bool = False

    def __post_init__(self) -> None:
        for name in (
            "transaction_price",
            "constrained_price",
            "estimated_total_cost",
            "costs_incurred_to_date",
            "billings_to_date",
        ):
            object.__setattr__(self, name, money(getattr(self, name)))
        if self.constrained_price > self.transaction_price:
            raise ValueError(f"{self.contract_id}: constrained price cannot exceed transaction price")


@dataclass(frozen=True)
class Measurement:
    contract_id: str
    poc: Decimal
    price: Decimal
    revenue_to_date: Decimal
    costs_to_date: Decimal
    estimated_total_loss: Decimal
    loss_provision: Decimal
    gross_profit_to_date: Decimal
    billings: Decimal
    contract_asset: Decimal
    contract_liability: Decimal
    cost_of_revenue: Decimal


def measure(contract: Contract) -> Measurement:
    price = contract.constrained_price
    if contract.timing is Timing.POINT_IN_TIME:
        revenue = price if contract.complete else Decimal("0.00")
        costs = contract.costs_incurred_to_date if contract.complete else Decimal("0.00")
        poc = Decimal("1.00") if contract.complete else Decimal("0.00")
        gp = money(revenue - costs)
        asset = money(max(revenue - contract.billings_to_date, Decimal("0")))
        liab = money(max(contract.billings_to_date - revenue, Decimal("0")))
        return Measurement(
            contract.contract_id,
            poc,
            price,
            revenue,
            costs,
            Decimal("0.00"),
            Decimal("0.00"),
            gp,
            contract.billings_to_date,
            asset,
            liab,
            costs,
        )

    if contract.estimated_total_cost <= 0:
        raise ValueError(f"{contract.contract_id}: estimated total cost must be positive")
    poc = (contract.costs_incurred_to_date / contract.estimated_total_cost).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    if poc > 1:
        poc = Decimal("1.0000")
    revenue = money(price * poc)
    estimated_profit = money(price - contract.estimated_total_cost)
    estimated_loss = money(-estimated_profit) if estimated_profit < 0 else Decimal("0.00")

    if estimated_loss > 0:
        # Cumulative GP must equal the full estimated loss (negative).
        gp = money(-estimated_loss)
        cost_of_revenue = money(revenue - gp)
        remaining_loss = money(
            estimated_loss
            - money(contract.costs_incurred_to_date - revenue)
        )
        if remaining_loss < 0:
            remaining_loss = Decimal("0.00")
        loss_provision = remaining_loss
    else:
        gp = money(revenue - contract.costs_incurred_to_date)
        cost_of_revenue = contract.costs_incurred_to_date
        loss_provision = Decimal("0.00")

    asset = money(max(revenue - contract.billings_to_date, Decimal("0")))
    liab = money(max(contract.billings_to_date - revenue, Decimal("0")))
    return Measurement(
        contract.contract_id,
        poc,
        price,
        revenue,
        contract.costs_incurred_to_date,
        estimated_loss,
        loss_provision,
        gp,
        contract.billings_to_date,
        asset,
        liab,
        cost_of_revenue,
    )
