import os
import appuifw

from filesel import FileSel
from window import Application, Dialog
from libmgr import LibManager
from reader import Reader


class VerboApp(Application):

    def __init__(self, app_dir="C:\\"):
        db_path = os.path.join(app_dir, u"verbo.e32dbm")
        appuifw.app.screen = "normal"

        self.lib_mgr = LibManager(db_path)
        self.book_list = []
        self.main_menu = [(u"Import book", self.add_book),
                            (u"Remove book", self.rm_book),
                            (u"Exit", self.close_app)]

        Application.__init__(self, u"Verbo", appuifw.Listbox([(u"",u"")], lambda:None), [])
        self.update_liblist()

    def update_liblist(self):
        self.book_list = self.lib_mgr.get_books()
        ob_callback = self.open_book

        if not self.book_list:
            self.book_list = [(u"Empty", u"add books by menu")]
            ob_callback = lambda: None

        self.set_ui(u"Verbo / Library",
                    appuifw.Listbox(self.book_list, ob_callback),
                    self.main_menu)
        self.refresh()

    def open_book(self):
        curr_book = appuifw.app.body.current()
        title = self.book_list[curr_book][0]
        path = self.book_list[curr_book][1]
        pos = self.lib_mgr.get_bookpos(path)

        def cbk():
            # when closing reader save last position 
            self.lib_mgr.update_book(path, title, dialog.currword_idx)
            self.refresh()
            return True

        dialog = Reader(cbk, title, path, pos)
        dialog.run()

    def add_book(self):
        dialog = FileSel(mask = r"(.*\.txt|.*\.fb2)")
        path = dialog.run()

        if path is not None:
            title = path.split("\\")[-1]
            #
            if self.lib_mgr.add_book(title, path):
                self.update_liblist()
            else:
                appuifw.note(u"That book already exists!", "error")

    def rm_book(self):
        curr_book = appuifw.app.body.current()
        # second item in book_list is path
        path = self.book_list[curr_book][1]
        self.lib_mgr.remove_book(path)
        self.update_liblist()

    def close_app(self):
        Application.close_app(self)
