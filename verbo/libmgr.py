import e32dbm


class LibManager(object):
    DB_PATH = u""

    def __init__(self, db_path):
        LibManager.DB_PATH = db_path
        self.db = e32dbm.open(LibManager.DB_PATH, "cf")

    def __del__(self):
        self.db.close()

    def add_book(self, title, path, pos=0):
        """ Check new book path in app cache (self.books).
            And if it not exists, add it.
            Args:
                title (unicode): book title
                path (unicode): full book path in filesystem
                pos (int): last reading position
            Returns:
                True or False depend on existing path in database
        """
        # lib can't contains books with the same path
        if path in self.db:
            return False

        # add it into db
        self.db[path] = u"%s,%s" % (title, unicode(pos))
        self.db.sync()

        return True

    def update_book(self, path, title, pos):
        self.db[path] = u"%s,%s" % (title, unicode(pos))
        self.db.sync()

    def remove_book(self, path):
        del self.db[path]
        self.db.sync()

    def get_books(self):
        """ Returns info for each book in library """
        return [(unicode(data.split(",")[0]), unicode(path))
                for path, data in self.db.items()]

    def get_bookpos(self, path):
        return int(self.db[path].split(",")[-1])
