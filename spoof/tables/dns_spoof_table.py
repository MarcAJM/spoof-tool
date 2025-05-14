import shelve

def get(domainname):
    with shelve.open("dns_spoof_table") as db:
        if domainname in db:
            return db[domainname]

def add(domainname: str, ip_address: str):
    with shelve.open("dns_spoof_table") as db:
        db[domainname] = ip_address

def remove(domainname: str):
     with shelve.open("dns_spoof_table") as db:
         if domainname in db:
             del db[domainname]

def remove_all():
    with shelve.open("dns_spoof_table") as db:
        db.clear()

def get_rows():
    rows = list()
    with shelve.open("dns_spoof_table") as db:
        for key in db.keys():
            rows.append((key, db[key]))
    return rows