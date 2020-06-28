import functools

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

import state
from book import Book

# ~ UI custom funcitons, wrappers and classes
# Wrappers
def callback(func):
    @functools.wraps(func)
    def wrapper(widget=None):
        return func()
    return wrapper

# Classes
class ObjectStorage:
    def __init__(self, builder):
        self._cache = {}
        self.builder = builder
    def __getitem__(self, key):
        if key not in self._cache:
            self._cache[key] = builder.get_object(key)
            if self._cache[key] is None:
                print("Warning: UI object not found: %s" % key)
        return self._cache[key]
    def __getattr__(self, key):
        return self[key]

# ~ Callbacks definition
@callback
def hide_add_popup():
    objects.add_book_window.hide()
    for key in Book.attributes:
        objects["add_%s_entry" % key.lower()].set_text("")

@callback
def hide_edit_popup():
    objects.edit_book_window.hide()
    for key in Book.attributes:
        objects["edit_%s_entry" % key.lower()].set_text("")

@callback
def show_add_popup():
    objects.add_book_window.show_all()
    objects.add_book_window.grab_focus()

@callback
def show_edit_popup():
    if not state.library.selected: return
    state.library.edited = state.library.selected
    for i, key in enumerate(Book.attributes):
        objects["edit_%s_entry" % key.lower()].set_text(state.library.bookstore[state.library.selected][i])
    objects.edit_book_window.show_all()
    objects.edit_book_window.grab_focus()

@callback
def confirm_edit():
    attrs = []
    for key in Book.attributes:
        attrs.append(objects["edit_%s_entry" % key.lower()].get_text())
    state.library.change_book(attrs)
    hide_edit_popup()
    
@callback
def remove_selected_book():
    state.library.remove_book()

@callback
def add_book():
    objects.add_book_window.hide()
    attrs = []
    for key in Book.attributes:
        entry = objects["add_%s_entry" % key.lower()]
        attrs.append(entry.get_text())
        entry.set_text("")
    state.library.add_book(attrs)

@callback
def remove_book():
    state.library.remove_book()

@callback
def save():
    state.library.save()

@callback
def reload():
    state.library.reload()
    
# ~ Interface
builder = Gtk.Builder()
builder.add_from_file(state.config["Application"]["file"])

objects = ObjectStorage(builder)


# ~ Binding callbacks
objects.main_window.connect("destroy", Gtk.main_quit)
objects.main_window.show_all()

# Toolbar buttons
objects.add_button.connect("clicked", show_add_popup)
objects.edit_button.connect("clicked", show_edit_popup)
objects.remove_button.connect("clicked", remove_selected_book)
objects.save_button.connect("clicked", save)
objects.reload_button.connect("clicked", reload)

# Diverse popup buttons
#  add_book_popup
objects.add_book_cancel_button.connect("clicked", hide_add_popup)
objects.add_book_confirm_button.connect("clicked", add_book)
#  edit_book_popup
objects.edit_book_cancel_button.connect("clicked", hide_edit_popup)
objects.edit_book_confirm_button.connect("clicked", confirm_edit)

# ~ Misc Operations
objects.main_window.maximize()
title = state.config["Application"].get("title", None)
if title:
    objects.main_window.set_title(title)
