
from app.tools import (
    compare_regimes,
    new_regime_tax_calculator,
    old_regime_tax_calculator,
)


def test_new_regime_tax_calculator():
    result = new_regime_tax_calculator(1000000)

    assert result["taxable_income"] == 1000000
    assert result["slab_tax"] == 40000
    assert result["total_tax"] == 0


def test_new_regime_rebate():
    result = new_regime_tax_calculator(1000000)

    assert result["rebate_87a"] == 40000
    assert result["tax_after_rebate"] == 0
    assert result["total_tax"] == 0


def test_old_regime_tax_calculator():
    result = old_regime_tax_calculator(700000)

    assert result["taxable_income"] == 700000
    assert result["slab_tax"] == 52500
    assert result["total_tax"] == 54600


def test_old_regime_rebate():
    result = old_regime_tax_calculator(500000)

    assert result["rebate_87a"] == 12500
    assert result["tax_after_rebate"] == 0
    assert result["total_tax"] == 0


def test_compare_regimes():
    result = compare_regimes(1000000, 700000)

    assert "new_regime" in result
    assert "old_regime" in result
    assert result["better_regime"] in ["new", "old", "equal"]
    assert result["tax_saving"] >= 0


def test_negative_income():
    result = new_regime_tax_calculator(-100000)

    assert result["taxable_income"] == 0
    assert result["total_tax"] == 0


def test_equal_regime_comparison():
    result = compare_regimes(0, 0)

    assert result["better_regime"] == "equal"
    assert result["tax_saving"] == 0
