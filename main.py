#!/usr/bin/python3

import gi, sys, configparser, sqlite3
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

cfg = configparser.ConfigParser()
cfg.read("config.ini")

sqlite3

class Book:
    attributes = [
        "Title",
        "Author",
        "Edition",
        "Collection",
        "ISBN"
    ]
    size = len(attributes) + 1
    def __init__(self, *args):
        if len(args) != self.size:
            raise ValueError("Required exactly %s attributes, got %s" % (self.size, len(args)))
        self.given = {key.lower(): value for key, value in zip(self.attributes, args[1:])}
        self.attrs = args[1:] + (args[0],)
    @property
    def tuple(self):
        return tuple(self.attrs)
    def __iter__(self):
        return iter(self.tuple)
    def __eq__(self, right):
        return self.tuple == right.tuple
    def __gt__(self, right):
        return self.tuple > right.tuple
    def __lt__(self, right):
        return self.tuple < right.tuple
    def __getattr__(self, key):
        return self.given[key]
    def __getitem__(self, key):
        return self.tuple[key]
    def __len__(self):
        return self.size

class Library:
    def __init__(self):
        self.init_db()
        self.load_books()
        self.init_treeview()
        
        self.search_entry = builder.get_object("search_entry")
        self.search_entry.connect("changed", self.refilter)

        add_book_cancel_button.connect("clicked", hide_add_popup)
        add_book_confirm_button.connect("clicked", self.add_book)

        edit_book_cancel_button.connect("clicked", hide_edit_popup)
        edit_book_confirm_button.connect("clicked", self.edit_book_do)

        save_button = builder.get_object("save_button")
        save_button.connect("clicked", self.save)

        reload_button = builder.get_object("reload_button")
        reload_button.connect("clicked", self.reload)
        
        self.load_treeview()

        self.save = True
    def init_db(self):
        self.connection = sqlite3.connect(cfg["Database"]["file"])
        self.cursor = self.connection.cursor()
        with open(cfg["Database"]["create_tables_script"]) as f:
            self.cursor.executescript(f.read())
        self.connection.commit()
    def init_treeview(self):
        self.treeview = builder.get_object("book_treeview")
        for i, column_title in enumerate(Book.attributes):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.treeview.append_column(column)
        self.init_selection()
    def init_selection(self):
        self.selection = self.treeview.get_selection()
        self.selection.connect("changed", self.on_selection_change)
        self.selected = None
    def load_treeview(self):
        self.search_filter = self.bookstore.filter_new()
        self.search_filter.set_visible_func(self._search_filter)
        self.sorted_bookstore = Gtk.TreeModelSort(model=self.search_filter)
        self.treeview.set_model(self.sorted_bookstore)
    def load_books(self):
        self.bookstore = Gtk.ListStore(str, str, str, str, str, int)
        with open(cfg["Database"]["query_entries_script"]) as f:
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
        return self.search_entry.get_text()
    def _search_filter(self, model, iter, data):
        text = self.search.lower()
        for field in model[iter]:
            if text in field.lower():
                return True
        return False
    def edit_book(self):
        if self.selected is None: return False
        self.edited = self.selected
        for i, key in enumerate(Book.attributes):
            builder.get_object("edit_%s_entry" % key.lower()).set_text(self.bookstore[self.selected][i])
        return True
    def edit_book_do(self, widget):
        attrs = []
        for i, key in enumerate(Book.attributes):
            text = builder.get_object("edit_%s_entry" % key.lower()).get_text()
            self.bookstore[self.edited][i] = text
            attrs.append(text)
        id = self.bookstore[self.edited][i+1]
        with open(cfg["Database"]["update_entry_script"]) as f:
            self.cursor.execute(f.read(), attrs + [id])
        hide_edit_popup(widget)
    def add_book(self, widget):
        add_book_window.hide()
        attrs = []
        for key in Book.attributes:
            entry = builder.get_object("add_%s_entry" % key.lower())
            attrs.append(entry.get_text())
            entry.set_text("")
        with open(cfg["Database"]["insert_entry_script"]) as f:
            id = self.cursor.execute(f.read(), attrs)
        self.bookstore.append(Book(id, *attrs))
        self.saved = False
    def remove_book(self, widget):
        if not self.selected: return
        id = self.bookstore[self.selected][Book.size-1]
        self.bookstore.remove(self.selected)
        with open(cfg["Database"]["remove_entry_script"]) as f:
            self.cursor.execute(f.read(), (id,))
        self.saved = False
            
builder = Gtk.Builder()
builder.add_from_file("window.glade")

window = builder.get_object("main_window")
window.connect("destroy", Gtk.main_quit)
window.show_all()

add_book_window = builder.get_object("add_book_window")
add_book_cancel_button = builder.get_object("add_book_cancel_button")
add_book_confirm_button = builder.get_object("add_book_confirm_button")

edit_book_window = builder.get_object("edit_book_window")
edit_book_cancel_button = builder.get_object("edit_book_cancel_button")
edit_book_confirm_button = builder.get_object("edit_book_confirm_button")


def hide_add_popup(widget):
        add_book_window.hide()
        for key in Book.attributes:
            builder.get_object("add_%s_entry" % key.lower()).set_text("")
def hide_edit_popup(widget):
    edit_book_window.hide()
    for key in Book.attributes:
        builder.get_object("edit_%s_entry" % key.lower()).set_text("")
def add_book_popup(widget):
    add_book_window.show_all()
    add_book_window.grab_focus()

def edit_book_popup(widget):
    if not library.edit_book():
        return
    edit_book_window.show_all()
    edit_book_window.grab_focus()
    
library = Library()

add_button = builder.get_object("add_button")
add_button.connect("clicked", add_book_popup)

edit_button = builder.get_object("edit_button")
edit_button.connect("clicked", edit_book_popup)

remove_button = builder.get_object("remove_button")
remove_button.connect("clicked", library.remove_book)

title = cfg["Application"].get("title", None)
if title:
    window.set_title(title)

window.maximize()

Gtk.main()
