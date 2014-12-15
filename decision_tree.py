import math
import copy
from collections import defaultdict
import war_data_parser
import pydot


class Node(object):
    prev_value = None
    attribute = None
    label = None
    depth = 0
    children = []
    win_loss_ties = ""

    def __init__(self, prev_value, attribute, label, win_loss_ties, depth, children):
        self.prev_value = prev_value
        self.attribute = attribute
        self.label = label
        self.depth = depth
        self.children = children
        self.win_loss_ties = win_loss_ties

    def __str__(self):
        return ("depth:%i label:%s parent value:%s feature:%s win/loss/ties:%s children:%s" %
                (self.depth, self.label, self.prev_value, self.attribute, self.win_loss_ties, str(self.children)))

    def __repr__(self):
        return ("depth:%i label:%s parent value:%s feature:%s win/loss/ties:%s children:%s" %
                (self.depth, self.label, self.prev_value, self.attribute, self.win_loss_ties, str(self.children)))

class Leaf(object):
    label = None
    depth = 0
    prev_value = None
    win_loss_ties = ""

    def __init__(self, prev_value, label, win_loss_ties, depth):
        self.prev_value = prev_value
        self.label = label
        self.depth = depth
        self.win_loss_ties = win_loss_ties

    def __str__(self):
        return "depth:%i label:%s parent value:%s win/loss/ties:%s" % (self.depth, self.label, self.prev_value, self.win_loss_ties)

    def __repr__(self):
        return "depth:%i label:%s parent value:%s win/loss/ties:%s" % (self.depth, self.label, self.prev_value, self.win_loss_ties)


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
            if item == "wina":
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
    win_count = sum([1 for instance in lst if instance == "1"])
    lose_count = sum([1 for instance in lst if instance == "0"])
    draw_count = sum([1 for instance in lst if instance == "-1"])

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

    win_count = len([instance for instance in lst if instance.label == "1"])
    lose_count = len([instance for instance in lst if instance.label == "-1"])
    draw_count = len([instance for instance in lst if instance.label == "0"])
    win_loss_ties = "%i/%i/%i" % (win_count, lose_count, draw_count)
    label = max([("1", win_count), ("-1", lose_count), ("0", draw_count)], key = lambda(label, count): count)[0]

    if win_count == len(lst) or lose_count == len(lst) or draw_count == len(lst):
        return Leaf(prev_value, label, win_loss_ties, depth)
    elif not attributes:
        return Leaf(prev_value, label, win_loss_ties, depth)
    elif depth == depth_restriction:
        return Leaf(prev_value, label, win_loss_ties, depth)
    else:
        next_decision_att, remaining = best_attribute(lst, attributes)
        children = []
        for value in att_dict[next_decision_att]:
            sub_lst = [instance for instance in lst if instance.data[next_decision_att] == value]
            if sub_lst:
                children.append(create_tree(value, sub_lst, depth+1, copy.deepcopy(remaining), att_dict, depth_restriction))
        return Node(prev_value, next_decision_att, label, win_loss_ties, depth, children)


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

        print "this is weirdly met %s %s" % (str(child), str(deciding_attribute))
        return t.label


def test(t, instances):
    correct = [instance for instance in instances if instance.label == predict_label(instance, t)]
    return float(len(correct))/len(instances)


def build_a_tree():
    parsed_data = war_data_parser.battle_object()
    battles = parsed_data.battles
    attribute_dict = parsed_data.kvs
    del attribute_dict["wina"]
    attributes = [attribute for (attribute, values) in attribute_dict.iteritems()]
    formatted = get_data(battles)
    tree = create_tree(None, formatted, 0, attributes, attribute_dict, 10)
    return tree


# Head is head of decision tree, name is the name of the picture for the file we want to output, ex "tree1"
def draw_tree(head, name):
    graph = pydot.Dot(graph_type="graph", ranksep="0.10")

    parent_node = pydot.Node(head.attribute)
    __add_children(head, parent_node, graph, 0)

    graph.write_png("%s.png" % name)


def __add_children(parent, parent_node, graph, no):
    for i, child in enumerate(parent.children):
        if child.prev_value == "":
            child.prev_value = "N/A"
        if child.label == "":
            child.label = "N/A"
        if isinstance(child, Node):
            child_node = pydot.Node(parent.attribute + child.attribute + str(parent.depth) + str(child.depth)
                                    + parent.win_loss_ties + child.win_loss_ties + str(no),
                                    label=child.attribute+"\nW/L/T: %s" % child.win_loss_ties)
            graph.add_node(child_node)
            edge = pydot.Edge(parent_node, child_node, label=child.prev_value)
            graph.add_edge(edge)
            __add_children(child, child_node, graph, no+i+1)
        else:
            leaf_node = pydot.Node(parent.attribute + child.label + str(parent.depth) + str(child.depth)
                                   + parent.win_loss_ties + child.win_loss_ties + str(no),
                                   label=child.label+"\nW/L/T: %s" % child.win_loss_ties)
            graph.add_node(leaf_node)
            edge = pydot.Edge(parent_node, leaf_node, label=child.prev_value)
            graph.add_edge(edge)


if __name__ == "__main__":
    head = build_a_tree()
    draw_tree(head, "tree")
    print head