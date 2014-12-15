import math
import copy
from collections import defaultdict
import war_data_parser

class Node(object):
    prev_value = None
    attribute = None
    label = None
    depth = 0
    children = []

    def __init__(self, prev_value, attribute, label, depth, children):
        self.prev_value = prev_value
        self.attribute = attribute
        self.label = label
        self.depth = depth
        self.children = children

    def __str__(self):
        return 'depth:%i label:%s parent value:%s feature:%s children%s' % (self.depth, self.label, self.prev_value, self.attribute, str(self.children))

    def __repr__(self):
        return 'depth:%i label:%s parent value:%s feature:%s children%s' % (self.depth, self.label, self.prev_value, self.attribute, str(self.children))


class Leaf(object):
    label = None
    depth = 0
    prev_value = None

    def __init__(self, prev_value, label, depth):
        self.prev_value = prev_value
        self.label = label
        self.depth = depth

    def __str__(self):
        return 'depth:%i label:%s parent value:%s' % (self.depth, self.label, self.prev_value)

    def __repr__(self):
        return 'depth:%i label:%s parent value:%s' % (self.depth, self.label, self.prev_value)


class Data(object):
    label = None
    data = None
    predicted_label = None

    def __init__(self, label, data):
        self.label = label
        self.data = data

#raw data is a list of dictionaries
#returns a list of Data objects
def get_data(raw_data):
    formatted = []
    for instance in raw_data:
        label = None
        data_dict = dict()
        for item, value in instance.iteritems():
            if item == 'wina':
                label = value
            else:
                data_dict[item] = value
        formatted.append(Data(label, data_dict))
    return formatted

#win, draw, lose are proportions
def entropy_helper(win, lose, draw):
    #0 log 0 = 0
    def log_helper(label):
        if label == 1 or label == 0:
            return 0
        else:
            return (label * (math.log(label, 2)))

    return (- log_helper(win) - log_helper(lose) - log_helper(draw))

#lst is a list of labels
def entropy(lst):
    count = len(lst)
    win_count = sum([1 for instance in lst if instance == '1'])
    lose_count = sum([1 for instance in lst if instance == '0'])
    draw_count = sum([1 for instance in lst if instance == '-1'])

    if count == 0:
        win_proportion = 0
        lose_proportion = 0
        draw_proportion = 0
    else:
        win_proportion = float(win_count)/count
        lose_proportion = float(lose_count)/count
        draw_proportion= float(draw_count)/count
    return entropy_helper(win_proportion, lose_proportion, draw_proportion)


#[(Label: string, value: string)] -> float
def information_gain(total_lst):
    original_count = len(total_lst)
    original_entropy = entropy([label for (label, value) in total_lst])

    #key is an attribute value, count is attributes of that value
    counts = defaultdict(int)
    labels = defaultdict(list)
    for label, value in total_lst:
        counts[value] += 1
        labels[value].append(label)
    new_entropy = sum([float(counts.get(item, 0.0))/original_count * entropy(lst) for (item, lst) in labels.iteritems()])
    return original_entropy - new_entropy


#input: [Data], [attributes, values] -> best_attribute, remaining_attributes
def best_attribute(data_lst, attribute_lst):
    attgain_lst = []
    for attribute in attribute_lst:
        reduced_lst = [(item.label, item.data[attribute]) for item in data_lst]
        attgain_lst.append((attribute, information_gain(reduced_lst)))
    max_attribute, info_gain = max(attgain_lst, key=lambda (attribute, info_gain): info_gain)
    attgain_lst.remove((max_attribute, info_gain))
    remaining_attributes = [attribute for (attribute, info_gain) in attgain_lst]
    return max_attribute, remaining_attributes


#lst is a lst of Data objects
def create_tree(prev_value, lst, depth, attributes, att_dict, depth_restriction=999999):

    win_count = len([instance for instance in lst if instance.label == '1'])
    lose_count = len([instance for instance in lst if instance.label == '-1'])
    draw_count = len([instance for instance in lst if instance.label == '0'])
    label = max([('1', win_count), ('-1', lose_count), ('0', draw_count)], key = lambda(label, count): count)[0]

    if win_count == len(lst) or lose_count == len(lst) or draw_count == len(lst):
        return Leaf(prev_value, label, depth)
    elif not attributes:
        return Leaf(prev_value, label, depth)
    else:
        next_decision_att, remaining = best_attribute(lst, attributes)
        children = []
        for value in att_dict[next_decision_att]:
            sub_lst = [instance for instance in lst if instance.data[next_decision_att] == value]
            if sub_lst:
                children.append(create_tree(value, sub_lst, depth+1, copy.deepcopy(remaining), att_dict, depth_restriction))
        return Node(prev_value, next_decision_att, label, depth, children)


def predict_label(instance, t):
    print str(instance.data)
    if type(t) == Leaf:
        print t.label
        print instance.label
        return t.label
    else:
        deciding_attribute = t.attribute
        for child in t.children:
            if child.prev_value == instance.data[deciding_attribute]:
                return predict_label(instance, child)

        print 'this is weirdly met %s %s' % (str(child), str(deciding_attribute))
        return t.label

def test(t, instances):
    correct = [instance for instance in instances if instance.label == predict_label(instance, t)]
    return float(len(correct))/len(instances)



def build_a_tree():

    parsed_data = war_data_parser.battle_object()
    battles = parsed_data.battles
    attribute_dict = parsed_data.kvs
    del attribute_dict['wina']
    attributes = [attribute for (attribute, values) in attribute_dict.iteritems()]
    formatted = get_data(battles)
    tree = create_tree(None, formatted, 0, attributes, attribute_dict, 9999)
    return tree

if __name__ == "__main__":
    print build_a_tree()