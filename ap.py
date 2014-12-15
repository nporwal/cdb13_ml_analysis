__author__ = 'Jeff'

from collections import defaultdict
import pickle
import random
import war_data_parser
import copy

class AveragedPerceptron(object):

    def __init__(self, weights_list):
        weights = dict()
        for key in weights_list:
            weights[key] = dict([('1', 0.0),('0', 0.0), ('-1', 0.0)])

        self.weights = weights
        self.averaged_weights = defaultdict(dict)
        self._totals = defaultdict(float)
        # The last time the feature was changed, for the averaging.
        self._tstamps = defaultdict(int)
        # Number of instances seen
        self.i = 0

    def predict(self, features):
        self.i += 1
        scores = defaultdict(float)
        for feat, value in features.iteritems():
            weights = self.weights[feat]
            for label, weight in weights.items():
                scores[label] += value * weight
            random.shuffle(scores)
        return max(scores.iteritems(), key = lambda (label, weight): weight)[0]


    def update(self, true_label, features, counts):
        '''Update the feature weights.'''

        for feat, value in features.iteritems():
            weights = self.weights[feat]
            for label, weight in weights.iteritems():
                feat_label = '%s,%s' % (feat, label)
                self._totals[feat_label] += ((self.i - self._tstamps[feat_label]) * weight)
                self._tstamps[feat_label] = self.i

                if label == true_label:
                    if label == "1":
                        weights[label] += 1
                        #weights[label] += float(counts['1'])/(counts[label])
                    elif label == "-1":
                        weights[label] += 2
                    elif label ==  "0":
                        weights[label] += 4
                else:
                    weights[label] -= 1



    def average_weights(self):
        '''Average weights from all iterations.'''
        for feature, weights in self.weights.items():
            for label, weight in weights.iteritems():
                feat_label = '%s,%s' % (feature, label)
                total = self._totals[feat_label]
                total += (self.i - self._tstamps[feat_label]) * weight
                averaged = round(total / float(self.i), 3)
                if averaged:
                    self.averaged_weights[feature][label] = averaged

    def save(self, path):
        '''Save the pickled model weights.'''
        return pickle.dump(dict(self.averaged_weights), open(path, 'w'))

    def load(self, path):
        '''Load the pickled model weights.'''
        self.weights = pickle.load(open(path))
        return None

def train(battles, attribute_list, counts, iterations):


    model = AveragedPerceptron(attribute_list)
    for i in range(0, iterations):
        random.shuffle(battles)
        for features, label in battles:

            prediction = model.predict(features)
            if prediction != label:
                model.update(label, features, counts)
    model.average_weights()
    #model.save(save_path)
    return model

def count_labels(instances):
    counts = dict()
    counts["total"] = len(instances)
    counts["1"] = len([label for features, label in instances if label == "1"])
    counts["-1"] = len([label for features, label in instances if label == "-1"])
    counts["0"] = len([label for features, label in instances if label == "0"])
    return counts

def sort_weights(weights):
    print weights.items()[0]
    sorted_wins = sorted(weights.iteritems(), key=lambda (k, w): w.get('1', 0.0))
    sorted_wins.reverse()

    sorted_ties = sorted(weights.iteritems(), key=lambda (k, w): w.get('0', 0.0))
    sorted_ties.reverse()

    sorted_losses = sorted(weights.iteritems(), key=lambda (k, w): w.get('-1', 0.0))
    sorted_losses.reverse()

    return sorted_wins, sorted_ties, sorted_losses

def test(model, instances):
    total = len(instances)
    correct = 0
    for data_dict, label in instances:
        for feat, value in data_dict.iteritems():
            scores = defaultdict(float)
            weights = model.averaged_weights[feat]
            for label, weight in weights.items():
                scores[label] += value * weight
            random.shuffle(scores)
        #print scores
        prediction = max(scores.iteritems(), key = lambda (label, weight): weight)[0]
        #print (str((prediction, label)) + '\n')
        if prediction == label:
            correct += 1
    return float(correct)/total

def kfold(data, attribute_list):
    random.shuffle(data)
    count = len(data)
    fold1 = copy.deepcopy(data[:count/4])
    fold2 = copy.deepcopy(data[count/4:count/2])
    fold3 = copy.deepcopy(data[count/2:count*3/4])
    fold4 = copy.deepcopy(data[count*3/4:])

    training1 = fold2 + fold3 + fold4
    counts1 = count_labels(training1)
    print (str(counts1) + '\n')
    model1 = train(training1, attribute_list, counts1, 5)
    pickle.dump(model1, open('model1', 'w'))
    accuracy1 = test(model1, fold1)

    training2 = fold1 + fold3 + fold4
    counts2 = count_labels(training2)
    print (str(counts2) + '\n')
    model2 = train(training2, attribute_list, counts2, 5)
    pickle.dump(model2, open('model2', 'w'))
    accuracy2 = test(model2, fold2)

    training3 = fold1 + fold2 + fold4
    counts3 = count_labels(training3)
    print (str(counts3) + '\n')
    model3 = train(training3, attribute_list, counts3, 5)
    pickle.dump(model1, open('model3', 'w'))
    accuracy3 = test(model3, fold3)

    training4 = fold1 + fold2 + fold3
    counts4 = count_labels(training4)
    print (str(counts4) + '\n')
    model4 = train(training4, attribute_list, counts4, 5)
    pickle.dump(model4, open('model4', 'w'))
    accuracy4 = test(model4, fold4)

    print "average accuracy: %f" % ((accuracy1 + accuracy2 + accuracy3 + accuracy4)/4)

def main():
    #adjust this to handle the format we preprocess the examples in
    def process(instance):
        data_dict = dict()
        for item, value in instance.iteritems():
            if item == "wina":
                label = value
            else:
                key = '%s,%s' % (item, value)
                data_dict[key] = 1

        return data_dict, label

    battles = war_data_parser.battle_object().battles
    attribute_dict =  war_data_parser.battle_object().kvs
    del attribute_dict["wina"]
    attribute_list = []
    battles = [process(instance) for instance in battles]
    for key, enums in attribute_dict.iteritems():
        for enum in enums:
            attribute_list.append('%s,%s' % (key, enum))

    kfold(battles, attribute_list)
    #counts = count_labels(battles)
    #model = train(battles, attribute_list, counts)
    #return sort_weights(model.averaged_weights)