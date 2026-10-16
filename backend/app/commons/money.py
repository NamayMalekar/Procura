def cents(x: float) -> int:
    """Money as whole cents, so comparisons never suffer from float rounding."""
    return int(round(x * 100))
