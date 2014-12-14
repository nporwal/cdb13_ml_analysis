import csv


def flatten(data):
    new_data = []
    for row in data:
        if len(row) > 1:
            d = {}
            for k in row[0].keys():
                s = ""
                for col in row:
                    if not col[k] in s:
                        s += col[k]
                d[k] = s
            new_data.append(d)
        else:
            new_data.append(row[0])
    return new_data


def parse_and_add(filename, n):
    data = [[] for _ in xrange(n)]
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[int(int(row["isqno"])-1)].append(row)
    return flatten(data)


class BattleData:
    # Provide filenames in order 'battles', 'weather', 'terrain'
    def __init__(self, filenames, keys_file):
        self.n = 0
        self.battles = []
        battles, filenames = filenames[0], filenames[1:]
        with open(battles) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["wina"] == "":
                    row["wina"] = -1
                self.battles.append(row)
                self.n += 1
        # Index of the arrays correspond to isqno-1

        weather = parse_and_add(filenames[0], self.n)
        terrain = parse_and_add(filenames[1], self.n)
        self.__combine(weather)
        self.__combine(terrain)
        self.__create_dict_and_strip(keys_file)

    def __combine(self, data):
        if len(data) != len(self.battles):
            raise Exception("arg data incorrect size")
        for i, b in enumerate(self.battles):
            row = data[i]
            for k, v in row.items():
                b[k] = v

    def __create_dict_and_strip(self, keys_file):
        with open(keys_file) as keys:
            self.kvs = {}
            for line in keys.readlines():
                key = line.strip()
                self.kvs[key] = []
        keys = self.kvs.keys()
        for battle in self.battles:
            for k, v in battle.items():
                if k in keys:
                    vals = self.kvs[k]
                    if not v in vals:
                        self.kvs[k].append(v)
                else:
                    del battle[k]
        for enum in self.kvs.values():
            enum.sort()

if __name__ == "__main__":
    battles = BattleData(["data/battles.csv", "data/weather.csv", "data/terrain.csv"], "data/keys.txt")