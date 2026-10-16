"""Business policy: the rules a buyer would write on a whiteboard. Change numbers here."""
import os


class Policy:
    def __init__(self):
        self.review_period_days = int(os.getenv("REVIEW_PERIOD_DAYS", 7))     # how often we can re-order
        self.approval_threshold = float(os.getenv("APPROVAL_THRESHOLD", 10000))  # $ above this needs a human
        self.accept_tolerance = 0.10          # recommendation within +-10% of real need is accepted as-is
        self.max_cover_factor = 1.25          # never end up above 125% of target stock
        self.min_supplier_reliability = 0.75  # suppliers below this are never used automatically
        self.max_proposal_attempts = 3        # tries the brain gets to pass the validator
        self.max_cycles = 3                   # propose -> act -> verify cycles before escalating


policy = Policy()
