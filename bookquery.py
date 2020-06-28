import isbnlib, book
import isbnlib.registry

services = [service for service in isbnlib.registry.services if service != "default"]

def query_by_isbn(isbn):
    data = {}
    for service in services:
        try:
            result = isbnlib.meta(isbn, service=service)
        except:
            continue
        todel = set()
        for key, value in result.items():
            if not value:
                todel.add(key)
        for key in todel:
            del result[key]
        data.update(result)
    attrs = {}
    for key, value in data.items():
        entry, function = book.Book.meta_map.get(key, (None, None))
        if entry == None: continue
        attrs[entry] = function(value)
    return attrs
