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
    data = []
    predicted_label = None

    def __init__(self, label, data):
        self.label = label
        self.data = data

#win, draw, lose are proportions
def entropy(win, lose, draw):
    #0 log 0 = 0
    if win  == 1 or lose == 1 or draw == 1:
        return 0
    return -(win * (math.log(win, 2))) - (lose * (math.log(lose, 2))) - (draw * (math.log(draw, 2)))


def information_gain_helper(lst):
    info = dict()
    info['count'] = len(lst)
    win_count
    lose_count
    draw_count
    if info['count'] == 0:
        info['win_proportion'] = 0
        info['lose_proportion'] = 0
        info ['draw_proportion'] = 0
    else:
        info['win_proportion'] = float(win_count)/info['count']
        info['lose_proportion'] = float(lose_count)/info['count']
        info ['draw_proportion'] = float(draw_count)/info['count']
    return info


#[(Label:Bool, Attribute:Bool)] -> float
def information_gain(total_lst):
    total = information_gain_helper(total_lst)

    #list of elements with attribute greater than the specified j
    greater_attribute_lst = [(label, attribute) for label, attribute in total_lst if attribute]
    greater = information_gain_helper(greater_attribute_lst)

    #list of elements with attribute less than the specified j
    lesser_attribute_lst = [(label, attribute) for label, attribute in total_lst if not attribute]
    lesser = information_gain_helper(lesser_attribute_lst)

    total_entropy = entropy(total['positive_proportion'], total['negative_proportion'])
    greater_entropy = ((float(greater['count'])/total['count'])
                       * entropy(greater['positive_proportion'], greater['negative_proportion']))
    lesser_entropy = ((float(lesser['count'])/total['count'])
                      * entropy(lesser['positive_proportion'], lesser['negative_proportion']))
    return total_entropy - greater_entropy - lesser_entropy


#input: [Data]
def best_combination(lst):
    result_lst = []
    for i in range(0, 9):
        for j in range(1, 10):
            criterion = information_gain([(instance.label, (instance.data[i] <= j)) for instance in lst])
            weight = 1 - criterion
            result_lst.append((weight, i, j))

    #min will first compare using weight, finding the lowest weight (highest criterion value)
    #then if there are ties, it will look for the lowest i (as required)
    #if there are further ties, it will look for the lowest j (as required)
    return min(result_lst)


def tree(lst, depth, depth_restriction=999999):
    weight, i, j = best_combination(lst)
    malignant_lst = [instance for instance in lst if instance.label]
    malignant_count = len(malignant_lst)
    benign_lst = [instance for instance in lst if not instance.label]
    benign_count = len(benign_lst)

    positive_lst = [instance for instance in lst if instance.data[i] <= j]
    negative_lst = [instance for instance in lst if instance.data[i] > j]

    #if information_gain == 0
    if weight == 1 or depth == depth_restriction:
        return Leaf(lst, malignant_count >= benign_count, depth)
    return Node(lst, malignant_count >= benign_count, depth, (i, j), tree(positive_lst, depth+1, depth_restriction), tree(negative_lst, depth+1, depth_restriction))


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
