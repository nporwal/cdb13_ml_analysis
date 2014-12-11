import csv

class Battle:
    def __init__(self, data, num):
        self.data = data
        self.n = num

def parse_battles(filename):
    data = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return (data[0].keys(), data)

def parse_and_add(filename, key, data):
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            i = row["isqno"]
            del row["isqno"]
            data[i][key] = row


if __name__ == "__main__":
    battles = parse_battles("data/battles.csv")
    parse_and_add("")
    for battle in battles[1]:
        print battle['isqno']