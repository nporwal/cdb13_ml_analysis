import math

class Node(object):
    label = None
    depth = 0
    children = []

    def __init__(self, label, depth, children):
        self.label = label
        self.depth = depth
        self.children = children


class Leaf(object):
    label = None
    depth = 0

    def __init__(self, label, depth):
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
        data_dict = None
        for item, value in instance.iteritems():
            if item == 'wina':
                label = value
            else:
                data_dict['item'] = value
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
    counts = dict()
    labels = dict()
    for label, value in total_lst:
        #we could fix this with default_dict, but we won't
        counts[value] = counts.get(value, 0) + 1
        labels[value] = labels[value].append(label)

    new_entropy = [counts[item]/original_count * entropy(lst) for (item, lst) in labels]
    return original_entropy - new_entropy


#input: [Data] -> best_attribute, remaining_attributes
def best_attribute(data_lst, attribute_lst):
    attgain_lst = []
    for attribute, enums in attribute_lst:
        reduced_lst = [(item.label, item.data['attribute']) for item in data_lst]
        attgain_lst.append(attribute, information_gain(reduced_lst))
    max_attribute, info_gain = max(attgain_lst, key=lambda (attribute, info_gain): info_gain)
    attgain_lst.remove(max)
    remaining_attributes = [attribute for (attribute, info_gain) in attgain_lst]
    return max_attribute, remaining_attributes


#lst is a lst of Data objects
def tree(lst, depth, attributes, att_dict, depth_restriction=999999):
    best, info_gain, remaining = best_attribute(lst, attributes)

    if info_gain == 1:
        pass
    else:
        children = []
        for value in att_dict[best]:
            sub_lst = [instance for instance in lst if instance.data['best'] == value]
            children.append(tree())
        Node(label, depth, children)

def water_tree(t, instances):
        the_type = type(t)
        if the_type == Leaf:
            for instance in instances:
                instance.predicted_label = t.label
            t.lst = instances
            return None
        t.lst = instances
        i, j = t.criterion
        positive_instances = [instance for instance in instances if instance.data[i] <= j]
        negative_instances = [instance for instance in instances if instance.data[i] > j]
        water_tree(t.left_child, positive_instances)
        water_tree(t.right_child, negative_instances)


def get_fruit(t):
    if type(t) == Leaf:
        return t.lst
    return get_fruit(t.left_child) + get_fruit(t.right_child)


def count_leaves(t):
    if type(t) == Leaf:
        return 1
    return count_leaves(t.left_child) + count_leaves(t.right_child)


def count_nodes(t):
    if type(t) == Leaf:
        return 1
    return 1 + count_nodes(t.left_child) + count_nodes(t.right_child)


def edible_proportion(instances):
    correct = [instance for instance in instances if instance.label == instance.predicted_label]
    return float(len(correct))/len(instances)


def string_tree(t):
    string_lst = str(t.lst)
    if type(t) == Leaf:
        return 'Leaf(list = %s)' % string_lst
    else:
        return ('Node(list = %s, left_child = %s, right_child = %s)' %
        (string_lst, string_tree(t.left_child), string_tree(t.right_child)))

def depth_calculations():
    print 'doing calculations of varying max depth'
    parsed = parsed_data('data/problem_2/bcan.train')
    for i in range(2, 21):
        print 'depth = %i' % i
        decision_t = tree(parsed, 1, depth_restriction=i)
        print 'leaves = %i' % count_leaves(decision_t)
        print 'nodes = %i' % count_nodes(decision_t)
        parsed2 = parsed_data('data/problem_2/bcan.test')
        water_tree(decision_t, parsed2)
        print edible_proportion(get_fruit(decision_t))
        print '\n'

if __name__ == '__main__':
    parsed = parsed_data('data/problem_2/bcan.train')
    decision_t = tree(parsed, 1)
    print 'leaves = %i' % count_leaves(decision_t)
    print 'nodes = %i' % count_nodes(decision_t)
    parsed2 = parsed_data('data/problem_2/bcan.test')
    water_tree(decision_t, parsed2)
    print 'done watering'
    print edible_proportion(get_fruit(decision_t))
    #print string_tree(decision_t) #I leave this evidence of my stupidity for all posterity
    print 'offset the i by 1'
    print "Parent node: %s" % str(decision_t.criterion)
    print "Child node: %s" % str(decision_t.left_child.criterion)
    print "Child node: %s" % str(decision_t.right_child.criterion)
    depth_calculations()
