#!/usr/bin/python3
import state
import ui
import library

state.library = library.Library()

ui.Gtk.main()
