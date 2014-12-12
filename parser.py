import csv


class BattleData:
    # Provide filenames in order 'battles', 'weather', 'durations', 'belligerents', 'dyads', 'terrain', 'widths'
    def __init__(self, filenames):
        self.n = 0
        self.battles = []
        battles, filenames = filenames[0], filenames[1:]
        with open(battles) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.battles.append(row)
                self.n += 1
        self.weather = [None] * self.n
        self.duration = [None] * self.n
        self.belligerents = d = [[] for _ in xrange(self.n)]
        self.terrain = [None] * self.n
        self.dyad = [None] * self.n
        self.width = [None] * self.n
        self.__keys = {
            'weather': self.weather,
            'durations': self.duration,
            'belligerents': self.belligerents,
            'dyads': self.dyad,
            'terrain': self.terrain,
            'widths': self.width
        }
        if len(filenames) != len(self.__keys):
            raise Exception("Not enough filenames provided, need to provide {} filenames".format(len(self.__keys)))

        keys = ['weather', 'durations', 'belligerents', 'dyads', 'terrain', 'widths']
        for i in range(len(self.__keys)):
            self.__parse_and_add(filenames[i], keys[i])

    def __parse_and_add(self, filename, key):
        data = self.__keys.get(key)
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if key == 'belligerents':
                    data[int(int(row["isqno"])-1)].append(row)
                else:
                    data[int(row["isqno"])-1] = row


if __name__ == "__main__":
    battles = BattleData(["data/battles.csv", "data/weather.csv", "data/battle_durations.csv", "data/belligerents.csv",
        "data/battle_dyads.csv", "data/terrain.csv", "data/front_widths.csv"])
    print battles.battles[0]
    print battles.belligerents[0]
    print battles.weather[0]
    print battles.duration[0]
    print battles.terrain[0]
    print battles.dyad[0]
    print battles.width[0]
