class Book:
    attributes = [
        "Title",
        "Author",
        "Edition",
        "Collection",
        "ISBN"
    ]
    meta_map = {
        "ISBN-13": ("ISBN", lambda x: x),
        "Title": ("Title", lambda x: x),
        "Authors": ("Author", lambda x: ", ".join(x)),
        "Publisher": ("Edition", lambda x: x),
        "Year": (None, None),
        "Language": (None, None),
        "ISBN-10": ("ISBN", lambda x: x)
    }
    size = len(attributes) + 1
    def __init__(self, *args):
        if len(args) != self.size:
            raise ValueError("Required exactly %s attributes, got %s" % (self.size, len(args)))
        self.attrs = args[1:] + (args[0],)
    @property
    def tuple(self):
        return tuple(self.attrs)
    def __iter__(self):
        return iter(self.tuple)
    def __eq__(self, right):
        return self.tuple == right.tuple
    def __hash__(self):
        return hash(self.tuple)
    def __gt__(self, right):
        return self.tuple > right.tuple
    def __lt__(self, right):
        return self.tuple < right.tuple
    def __getitem__(self, key):
        return self.tuple[key]
    def __len__(self):
        return self.size

