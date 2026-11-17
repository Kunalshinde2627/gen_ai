CESS_RATE = 0.04

# (upper limit of the slab, tax rate). None means "no upper limit".
NEW_SLABS = [
    (400000, 0.00), (800000, 0.05), (1200000, 0.10), (1600000, 0.15),
    (2000000, 0.20), (2400000, 0.25), (None, 0.30),
]
OLD_SLABS = [(250000, 0.00), (500000, 0.05), (1000000, 0.20), (None, 0.30)]


def _slab_breakdown(taxable_income, slabs):
    """Tax for each slab that the income reaches."""
    rows, lower = [], 0
    for upper, rate in slabs:
        top = taxable_income if upper is None else min(taxable_income, upper)
        amount = max(top - lower, 0)
        if amount > 0:
            rows.append({
                "slab": f"{lower:,} to {'above' if upper is None else format(upper, ',')}",
                "rate_percent": round(rate * 100),
                "income_in_slab": amount,
                "tax": round(amount * rate),
            })
        if upper is None:
            break
        lower = upper
    return rows


def _compute(taxable_income, slabs, rebate_limit, rebate_max, marginal_relief):
    taxable_income = max(int(taxable_income), 0)
    breakdown = _slab_breakdown(taxable_income, slabs)
    slab_tax = sum(row["tax"] for row in breakdown)

    rebate = min(slab_tax, rebate_max) if taxable_income <= rebate_limit else 0
    tax_after_rebate = slab_tax - rebate

    note = ""
    if marginal_relief and taxable_income > rebate_limit:
        extra_income = taxable_income - rebate_limit
        if tax_after_rebate > extra_income:
            tax_after_rebate = extra_income
            note = "Marginal relief: tax is limited to the income above the rebate limit."

    cess = round(tax_after_rebate * CESS_RATE)
    return {
        "taxable_income": taxable_income,
        "breakdown": breakdown,
        "slab_tax": slab_tax,
        "rebate_87a": rebate,
        "tax_after_rebate": tax_after_rebate,
        "cess_4_percent": cess,
        "total_tax": tax_after_rebate + cess,
        "note": note,
    }


def new_regime_tax_calculator(taxable_income):
    """New regime (AY 2026-27). Input is TAXABLE income: salary minus Rs 75,000 standard deduction.

    87A rebate: no tax up to Rs 12 lakh taxable income. Then 4% cess.
    """
    return _compute(taxable_income, NEW_SLABS, 1200000, 60000, marginal_relief=True)


def old_regime_tax_calculator(taxable_income):
    """Old regime. Input is TAXABLE income: salary minus Rs 50,000 standard deduction, 80C, 80D, HRA.

    87A rebate: up to Rs 12,500 if taxable income is up to Rs 5 lakh. Then 4% cess.
    """
    return _compute(taxable_income, OLD_SLABS, 500000, 12500, marginal_relief=False)


def compare_regimes(new_taxable_income, old_taxable_income):
    """Tax in both regimes and which one is lower. Each regime has its own taxable income."""
    new = new_regime_tax_calculator(new_taxable_income)
    old = old_regime_tax_calculator(old_taxable_income)
    return {
        "new_regime_total_tax": new["total_tax"],
        "old_regime_total_tax": old["total_tax"],
        "better_regime": "new" if new["total_tax"] <= old["total_tax"] else "old",
    }