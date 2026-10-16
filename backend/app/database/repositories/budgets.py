from ._base import Repo


class BudgetRepo(Repo):
    def get(self, category):
        return self.one("SELECT * FROM budgets WHERE category=?", (category,))

    def all(self):
        return self.many("SELECT * FROM budgets ORDER BY category")

    def adjust(self, category, delta):
        """delta < 0 spends budget, delta > 0 gives it back."""
        self.run("UPDATE budgets SET remaining = ROUND(remaining + ?, 2) WHERE category=?", (delta, category))
