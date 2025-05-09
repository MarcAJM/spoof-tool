import shelve

def add(ip1, ip2):
    with shelve.open("target_links_table") as db:
        key = get_key(ip1, ip2)
        db[key] = [ip1, ip2]

def remove(ip1, ip2):
    with shelve.open("target_links_table") as db:
        key = get_key(ip1, ip2)
        if key in db:
            del db[key]

def remove_all():
    with shelve.open("target_links_table") as db:
        db.clear()

def get_all():
    with shelve.open("target_links_table") as db:
        return list(db.values())

def get_key(ip1, ip2):
    return ip1 + '_' + ip2

