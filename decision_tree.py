import math
import copy
from collections import defaultdict

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


class Leaf(object):
    label = None
    depth = 0
    prev_value = None

    def __init__(self, prev_value, label, depth):
        self.prev_value = prev_value
        self.label = label
        self.depth = depth


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
    if win  == 1 or lose == 1 or draw == 1:
        return 0
    return -(win * (math.log(win, 2))) - (lose * (math.log(lose, 2))) - (draw * (math.log(draw, 2)))

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


def string_tree(t):
    string_lst = str(t.lst)
    if type(t) == Leaf:
        return 'Leaf(list = %s)' % string_lst
    else:
        return ('Node(list = %s, left_child = %s, right_child = %s)' %
        (string_lst, string_tree(t.left_child), string_tree(t.right_child)))


if __name__ == '__main__':
    test_seed1 = dict([('wina', '-1'), ('feature1', 'a')])
    test_seed2 = dict([('wina', '1'), ('feature1', 'b')])
    test_seed3 = dict([('wina', '0'), ('feature1', 'c')])
    test_data = [test_seed1, test_seed2, test_seed3]
    test_attributes = ['feature1']
    test_attribute_dict = dict([('feature1', ['a', 'b', 'c'])])

    formatted = get_data(test_data)
    tree = create_tree(None, formatted, 0, test_attributes, test_attribute_dict, 9999)

    print test(tree, formatted)