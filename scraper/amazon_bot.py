import json
import ipdb

def get_key(address):
    return "".join(address["street"].split()) + "$" + address["zipcode"]

if __name__ == '__main__':
    with open("../page.json", "r") as f:
        keyset = set()
        items = json.loads(f.read())

        for item in items:
            key = item["url"]
            keyset.add(key)

    print("unique keys: " + str(len(keyset)))
    