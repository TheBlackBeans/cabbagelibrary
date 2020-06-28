import sqlite3
import state, ui
from book import Book

class Library:
    def __init__(self):
        self.init_db()
        self.load_books()
        self.init_treeview()

        ui.objects.search_entry.connect("changed", self.refilter)

        self.load_treeview()

        self.saved = True
    def init_db(self):
        self.connection = sqlite3.connect(state.config["Database"]["file"])
        self.cursor = self.connection.cursor()
        with open(state.config["Database"]["create_tables_script"]) as f:
            self.cursor.executescript(f.read())
        self.connection.commit()
    def init_treeview(self):
        for i, column_title in enumerate(Book.attributes):
            renderer = ui.Gtk.CellRendererText()
            column = ui.Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            ui.objects.book_treeview.append_column(column)
        self.init_selection()
    def init_selection(self):
        self.selection = ui.objects.book_treeview.get_selection()
        self.selection.connect("changed", self.on_selection_change)
        self.selected = None
    def load_treeview(self):
        self.search_filter = self.bookstore.filter_new()
        self.search_filter.set_visible_func(self._search_filter)
        self.sorted_bookstore = ui.Gtk.TreeModelSort(model=self.search_filter)
        ui.objects.book_treeview.set_model(self.sorted_bookstore)
    def load_books(self):
        self.bookstore = ui.Gtk.ListStore(*(str for i in range(Book.size-1)), int)
        with open(state.config["Database"]["query_entries_script"]) as f:
            for attrs in self.cursor.execute(f.read()):
                self.bookstore.append(Book(*attrs))
    def save(self, widget=None):
        self.saved = True
        self.connection.commit()
    def reload(self, widget=None):
        self.saved = True
        self.init_db()
        self.load_books()
        self.load_treeview()
    def on_selection_change(self, selection):
        _, iter = selection.get_selected()
        self.selected = iter if iter is None else self.search_filter.convert_iter_to_child_iter(self.sorted_bookstore.convert_iter_to_child_iter(iter))
    def refilter(self, widget):
        self.search_filter.refilter()
    @property
    def search(self):
        return ui.objects.search_entry.get_text()
    def _search_filter(self, model, iter, data):
        text = self.search.lower()
        for field in model[iter]:
            if text in str(field).lower():
                return True
        return False
    def change_book(self, attrs):
        for i, text in enumerate(attrs):
            self.bookstore[self.edited][i] = text
        id = self.bookstore[self.edited][i+1]
        with open(state.config["Database"]["update_entry_script"]) as f:
            self.cursor.execute(f.read(), attrs + [id])
    def add_book(self, attrs):
        with open(state.config["Database"]["insert_entry_script"]) as f:
            self.cursor.execute(f.read(), attrs)
        id = self.cursor.lastrowid
        self.bookstore.append(Book(id, *attrs))
        self.saved = False
    def remove_book(self):
        if not self.selected: return
        id = self.bookstore[self.selected][Book.size-1]
        self.bookstore.remove(self.selected)
        with open(state.config["Database"]["remove_entry_script"]) as f:
            self.cursor.execute(f.read(), (id,))
        self.saved = False
