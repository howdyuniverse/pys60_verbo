import e32dbm


class LibManager(object):
    DB_PATH = u""

    def __init__(self, db_path):
        LibManager.DB_PATH = db_path
        self.db = e32dbm.open(LibManager.DB_PATH, "cf")

    def __del__(self):
        self.db.close()

    def add_book(self, title, path):
        """ Check new book path in app cache (self.books).
            And if it not exists, add it.
        """
        # lib can't contains books with the same path
        if path in self.db:
            return False

        # add it into db
        self.db[path] = title
        self.db.sync()

        return True

    def remove_book(self, path):
        del self.db[path]
        self.db.sync()

    def get_books(self):
        """ Returns info for each book in library """
        books = [(unicode(t), unicode(p)) for p, t in self.db.items()]
        if not books:
            return [(u"Empty", u"add books by menu")]
        return books
