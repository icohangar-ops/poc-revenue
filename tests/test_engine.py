from decimal import Decimal

from poc_revenue.engine import Contract, Timing, measure
from poc_revenue.evidence import evidence_pack


def test_cost_to_cost_profitable() -> None:
    c = Contract(
        "JOB-1",
        "installation",
        Timing.OVER_TIME,
        transaction_price="1000000",
        constrained_price="1000000",
        estimated_total_cost="800000",
        costs_incurred_to_date="200000",
        billings_to_date="300000",
    )
    m = measure(c)
    assert m.poc == Decimal("0.2500")
    assert m.revenue_to_date == Decimal("250000.00")
    assert m.contract_liability == Decimal("50000.00")
    assert m.contract_asset == Decimal("0.00")
    assert m.estimated_total_loss == Decimal("0.00")
    assert m.gross_profit_to_date == Decimal("50000.00")


def test_variable_consideration_is_constrained() -> None:
    c = Contract(
        "JOB-2",
        "bonus uncertain",
        Timing.OVER_TIME,
        transaction_price="1200000",
        constrained_price="1000000",
        estimated_total_cost="800000",
        costs_incurred_to_date="400000",
        billings_to_date="0",
    )
    m = measure(c)
    assert m.price == Decimal("1000000.00")
    assert m.poc == Decimal("0.5000")
    assert m.revenue_to_date == Decimal("500000.00")


def test_onerous_contract_accrues_full_loss() -> None:
    c = Contract(
        "JOB-3",
        "loss job",
        Timing.OVER_TIME,
        transaction_price="1000000",
        constrained_price="1000000",
        estimated_total_cost="1200000",
        costs_incurred_to_date="300000",
        billings_to_date="0",
    )
    m = measure(c)
    assert m.poc == Decimal("0.2500")
    assert m.revenue_to_date == Decimal("250000.00")
    assert m.estimated_total_loss == Decimal("200000.00")
    assert m.gross_profit_to_date == Decimal("-200000.00")
    # incurred loss 50k already in costs-revenue; remaining 150k is the provision
    assert m.loss_provision == Decimal("150000.00")
    assert m.cost_of_revenue == Decimal("450000.00")


def test_point_in_time_recognizes_only_when_complete() -> None:
    open_c = Contract(
        "PIT-1", "equipment", Timing.POINT_IN_TIME,
        "50000", "50000", "30000", "10000", "0", complete=False,
    )
    done = Contract(
        "PIT-2", "equipment", Timing.POINT_IN_TIME,
        "50000", "50000", "30000", "30000", "50000", complete=True,
    )
    assert measure(open_c).revenue_to_date == Decimal("0.00")
    assert measure(done).revenue_to_date == Decimal("50000.00")
    assert measure(done).contract_liability == Decimal("0.00")


def test_evidence_pack() -> None:
    c = Contract(
        "JOB-1", "x", Timing.OVER_TIME, "1000000", "1000000", "800000", "200000", "0"
    )
    pack = evidence_pack((measure(c),), "H1 2026", "Controller")
    assert pack["revenue_to_date"] == "250000.00"
    assert pack["control_id"] == "ICFR-ASC606-01"
    assert pack["lock_state"] == "LOCKED"
    assert pack["is_evidence"] is True


def test_unsigned_pack_is_exploring_not_evidence() -> None:
    c = Contract(
        "JOB-1", "x", Timing.OVER_TIME, "1000000", "1000000", "800000", "200000", "0"
    )
    pack = evidence_pack((measure(c),), "H1 2026", "")
    assert pack["lock_state"] == "EXPLORING"
    assert pack["is_evidence"] is False
