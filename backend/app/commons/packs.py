def floor_pack(q: int, pack: int) -> int:
    return (int(q) // pack) * pack


def ceil_pack(q: int, pack: int) -> int:
    return -(-int(q) // pack) * pack
