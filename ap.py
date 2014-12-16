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


    def update(self, true_label, features):
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


def train(battles, attribute_list, iterations):
    model = AveragedPerceptron(attribute_list)
    for i in range(0, iterations):
        random.shuffle(battles)
        for features, label in battles:

            prediction = model.predict(features)
            if prediction != label:
                model.update(label, features)
    model.average_weights()
    return model


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
        if scores:
            prediction = max(scores.iteritems(), key = lambda (label, weight): weight)[0]
        else:
            prediction = random.shuffle(["1", "0", "-1"])
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
    model1 = train(training1, attribute_list, 5)
    pickle.dump(model1, open('model1', 'w'))
    accuracy1 = test(model1, fold1)

    training2 = fold1 + fold3 + fold4
    model2 = train(training2, attribute_list, 5)
    pickle.dump(model2, open('model2', 'w'))
    accuracy2 = test(model2, fold2)

    training3 = fold1 + fold2 + fold4
    model3 = train(training3, attribute_list, 5)
    pickle.dump(model1, open('model3', 'w'))
    accuracy3 = test(model3, fold3)

    training4 = fold1 + fold2 + fold3
    model4 = train(training4, attribute_list, 5)
    pickle.dump(model4, open('model4', 'w'))
    accuracy4 = test(model4, fold4)

    return (accuracy1 + accuracy2 + accuracy3 + accuracy4)/4.0

if __name__ == "__main__":
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

    model = train(battles, attribute_list, 5)
    sorted_wins, sorted_ties, sorted_losses = sort_weights(model.averaged_weights)
    print "features with the heaviest weight for attacker's win:\n"
    for i in range(0, 5):
        print str(sorted_wins[i])
        print '\n'

    print "features with the heaviest weight for attacker's loss:\n"
    for i in range(0, 5):
        print str(sorted_losses[i])
        print '\n'

    print "features with the heaviest weight for tie:\n"
    for i in range(0, 5):
        print str(sorted_ties[i])
        print '\n'