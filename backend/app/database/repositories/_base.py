class Repo:
    """Tiny base class: holds the connection and turns rows into plain dicts."""

    def __init__(self, conn):
        self.conn = conn

    def one(self, sql, args=()):
        r = self.conn.execute(sql, args).fetchone()
        return dict(r) if r else None

    def many(self, sql, args=()):
        return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def run(self, sql, args=()):
        self.conn.execute(sql, args)
        self.conn.commit()
