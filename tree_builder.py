from parser import analyze_expression
import pydot
import copy
from itertools import count, permutations, product
from collections import Counter, OrderedDict



def drow_tree(expr, index):
    tree = pydot.Dot(graph_type='graph')
    c = count(0)

    def add_elements(expr, tree):
        if len(expr) > 1:
            op_node = pydot.Node(c.next(), label=expr[1])
            left_child = add_elements(expr[0], tree)
            right_child = add_elements(expr[2], tree)
            tree.add_node(op_node)
            tree.add_edge(pydot.Edge(op_node, left_child))
            tree.add_edge(pydot.Edge(op_node, right_child))
            return op_node
        else:
            node = pydot.Node(c.next(), label=expr[0])
            tree.add_node(node)
            return node

    core = add_elements(expr, tree)
    tree.write_png('my_tree%s.png' % index)
            


def get_new_expr_for_return(new_expr, was_modified):
    if len(new_expr) > 1 or (len(new_expr) == 1 and was_modified):
        new_expr = new_expr
    else:
        new_expr = new_expr[0]
    return new_expr

def replace_operation(op):
    if op == '/':
        op = '*'
    elif op == '-':
        op = '+'
    return op

def modify_expr_mull_plus(expr, op):
    new_expr = []

    couple = []
    finish_couple = False
    was_modified = False
    for indx, item in enumerate(expr):
        is_not_last = indx+1 < len(expr)

        if finish_couple:
            new_expr.append(item)
            finish_couple = False
            continue
        if len(couple) == 0:
            if is_not_last and expr[indx+1] == op:
                if type(item) == list:
                    tmp , new_wmod = modify_expr_mull_plus(item, op)
                    was_modified = was_modified or new_wmod
                    couple.append(tmp)
                else:
                    couple.append(item)
            else:
                if type(item) == list:
                    item, new_wmod = modify_expr_mull_plus(item, op)
                    was_modified = was_modified or new_wmod
                new_expr.append(item)
                finish_couple = True
                continue
        elif len(couple) == 1:
            need_op = item == op
            couple.append(item)
        elif len(couple) == 2:
            if type(item) == list:
                tmp, new_wmod = modify_expr_mull_plus(item, op)
                was_modified = was_modified or new_wmod
                couple.append(tmp)
            else:
                couple.append(item)

        if len(couple) == 3:
            if is_not_last or len(expr)>3:
                new_expr.append(couple)
                was_modified = True
            else:
                for c in couple:
                    new_expr.append(c)
            finish_couple = True
            couple = []
    if len(couple):
        for c in couple:
            new_expr.append(c)
    return get_new_expr_for_return(new_expr, was_modified), was_modified

def modify_expr_div_min(expr, op):
    new_expr = []

    couple = []
    finish_couple = False
    was_modified = False
    for indx, item in enumerate(expr):
        is_not_last = indx+1 < len(expr)
        
        if finish_couple:
            new_expr.append(item)
            finish_couple = False
            continue
        if len(couple) == 0:
            if is_not_last and expr[indx+1] == op:
                if type(item) == list:
                    tmp , new_wmod = modify_expr_div_min(item, op)
                    was_modified = was_modified or new_wmod
                    couple.append(tmp)
                else:
                    couple.append(item)
                is_not_first = indx > 0
            else:
                if type(item) == list:
                    item, new_wmod = modify_expr_div_min(item, op)
                    was_modified = was_modified or new_wmod
                new_expr.append(item)
                continue
        elif len(couple) == 1:
            if is_not_first and new_expr[-1] == op:
                item = replace_operation(item)
            couple.append(item)
        elif len(couple) == 2:
            if type(item) == list:
                tmp , new_wmod = modify_expr_div_min(item, op)
                was_modified = was_modified or new_wmod
                couple.append(tmp)
            else:
                couple.append(item)

        if len(couple) == 3:
            if is_not_last or len(expr)>3:
                new_expr.append(couple)
                was_modified = True
            else:
                for c in couple:
                    new_expr.append(c)
            finish_couple = True
            couple = []
    if len(couple):
        for c in couple:
            new_expr.append(c)
    return get_new_expr_for_return(new_expr, was_modified), was_modified

def set_brackets(nx):
    was_modified = True
    while was_modified:
        nx, was_modified = modify_expr_div_min(nx, '/')
    
    was_modified = True
    while was_modified:
        nx, was_modified = modify_expr_mull_plus(nx, '*')
    
    was_modified = True
    while was_modified:
        nx, was_modified = modify_expr_div_min(nx, '-')
    
    was_modified = True
    while was_modified:
        nx, was_modified = modify_expr_mull_plus(nx, '+')
    return nx


def set_fake_brackets(expr):
    new_expr = []
    term = []
    finish_term = False

    for indx, item in enumerate(expr):
        is_not_last = indx+1 < len(expr)
        if finish_term:
            new_expr.append(item)
            finish_term = False
            continue
        if len(term) == 0 or len(term)%2 == 0:
            if is_not_last and expr[indx+1] in ['*', '/']:
                if type(item) == list:
                    item = set_fake_brackets(item)
                term.append(item)
            else:
                if is_not_last and term:
                    term.append(item)
                    new_expr.append(term)
                    term = []
                    finish_term = True
                    continue
                else:
                    if not term:
                        new_expr.append(item)
                    else:
                        term.append(item)
                        new_expr.append(term)

        elif len(term)%2 != 0:
            term.append(item)
    return new_expr if len(new_expr) > 3 else new_expr[0]

def get_weight(item):
    res = 0
    weights = {
        '+': 2,
        '-': 2,
        '*': 3,
        '/': 5,
    }
    def get_weight_for_list(expr):
        res = 0
        for indx in range(1, len(expr), 2):
            if type(expr[indx+1]) == list:
                res += get_weight_for_list(expr[indx+1])
            res += weights[expr[indx]]
            
        return res

    if type(item[1]) == list:
        res = get_weight_for_list(item[1])
    
    # don't culculate '+'' or '-'' operation before operand
    # if item[0] in weights:
    #     res += weights[item[0]]
    return res

def get_sign_index(expr, el):
    index = expr.index(el)
    return index-1

def sorting(expr):
    expr = convert_to_tuples(expr)
    for indx in range(len(expr)):
        max_wel = max(expr[:len(expr)-(indx)], key=get_weight)
        if type(max_wel[1]) != list:
            break
        expr.insert(len(expr)-indx, max_wel)
        expr.remove(max_wel)

    return expr

def convert_to_tuples(expr_list):
    res = []
    expr.insert(0, '+')
    for index in range(0,len(expr_list),2):
        res.append((expr_list[index], expr_list[index+1]))
    return res

def permutation(expr):
    result = []
    weight_table = OrderedDict()

    # expr = convert_to_tuples(expr)

    for item in expr:
        weight = get_weight(item)
        if weight in weight_table:
            weight_table[weight].append(item)
        else:
            weight_table[weight] = [item]
    # print "weight_table"
    # for key, value in weight_table.iteritems():
    #     print key, value

    for key, value in weight_table.iteritems():
        if key > 0 and len(value) > 1:
            weight_table[key] = map(list, permutations(value))

    # print "with permutation"
    # for key, value in weight_table.iteritems():
        # print key, value

    if 0 in weight_table:
        # begin = weight_table[0]
        result.append(weight_table[0])
        # print result

    del weight_table[0]
            
    for key, value in weight_table.iteritems():
        if len(value) < 2:
            result = map(lambda x: x+value, result)
        else:
            result = map(list,product(result, value))
            result = map(lambda x: x[0]+x[1], result)
            
    # for index, var in enumerate(result):
    #     print 'Variant N%s' % index
    #     print var
    return result



if __name__ == "__main__":
    global new_expr
    expr_list = analyze_expression()
    expr = set_fake_brackets(expr_list)
    print expr
    expr = sorting(expr)
    expr = permutation(expr)
    print "!!!!!\n",expr
    # permutation(expr)
    # expr_with_wight = set_wight(expr_list)
    # nx = set_brackets(expr) 
    # print 'Result: ', nx
    for index, var in enumerate(expr):
        print 'Variant N%s' % index
        tmp_expr = []
        print "44444", var
        for item in var:
            tmp_expr += item
        print tmp_expr
        tmp_expr = set_brackets(tmp_expr[1:])
        drow_tree(tmp_expr, index)
    # drow_tree(nx)


