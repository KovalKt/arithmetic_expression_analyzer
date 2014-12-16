from parser import analyze_expression
import pydot
import copy
from itertools import count, permutations, product
from collections import Counter, OrderedDict



# def drow_tree(expr, index):
#     tree = pydot.Dot(graph_type='graph')
#     c = count(0)

#     def add_elements(expr, tree):
#         indx = c.next()
#         if len(expr) > 1:
#             op_node = pydot.Node(indx, label="%s (%s)"%(expr[1], indx))
#             left_child = add_elements(expr[0], tree)
#             right_child = add_elements(expr[2], tree)
#             tree.add_node(op_node)
#             tree.add_edge(pydot.Edge(op_node, left_child))
#             tree.add_edge(pydot.Edge(op_node, right_child))
#             return op_node
#         else:
#             node = pydot.Node(indx, label="%s (%s)"%(expr[0], indx))
#             tree.add_node(node)
#             return node

#     core = add_elements(expr, tree)
#     tree.write_png('my_tree%s.png' % index)
            


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
        # print indx, item, 'is_not_last ', is_not_last
        if finish_term:
            new_expr.append(item)
            finish_term = False
            # print 'finish term'
            continue
        if len(term) == 0 or len(term)%2 == 0:
            # print 'len term ', len(term)
            if is_not_last and expr[indx+1] in ['*', '/']:
                if type(item) == list:
                    item = set_fake_brackets(item)
                # print '00000000', item
                term.append(item)
            else:
                # print 'else111'
                if is_not_last and term:
                    term.append(item)
                    new_expr.append(term)
                    # print '111111111111', term, new_expr
                    term = []
                    finish_term = True
                    continue
                else:
                    if not term:
                        # print '222222222'
                        new_expr.append(item)
                        # print indx, item
                        finish_term = True
                        continue
                    else:
                        term.append(item)
                        new_expr.append(term)
                        # print '33333333333333333333333', term, new_expr
                        finish_term = True
                        continue

        elif len(term)%2 != 0:
            # print 'some strangue elif'
            term.append(item)
    return new_expr if len(new_expr) >= 3 else new_expr[0]

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
    expr_list.insert(0, '+')
    for index in range(0,len(expr_list),2):
        res.append((expr_list[index], expr_list[index+1]))
    return res

def permutation(expr):
    result = []
    weight_table = OrderedDict()

    for item in expr:
        weight = get_weight(item)
        if weight in weight_table:
            weight_table[weight].append(item)
        else:
            weight_table[weight] = [item]

    for key, value in weight_table.iteritems():
        if key > 0 and len(value) > 1:
            weight_table[key] = map(list, permutations(value))

    if 0 in weight_table:
        result.append(weight_table[0])

    del weight_table[0]
            
    for key, value in weight_table.iteritems():
        if len(value) < 2:
            result = map(lambda x: x+value, result)
        else:
            result = map(list,product(result, value))
            result = map(lambda x: x[0]+x[1], result)
            
    return result

def mull_div(el1, el2, op):
    if el1[0] == '+' and el2[0] == '+':
        return ['+', el1[1], op, el2[1]]
    elif el1 [0] == '-' and el2[0] == '-':
        return ['+', el1[1], op, el2[1]]
    elif el1[0] == '-' or el2[0] == '-':
        return ['-', el1[1], op, el2[1]]

def open_brakets(expr):
    # print ',,,,,,,,,,'
    result = []
    was_opened = False
    step_plus = False
    expr = convert_to_tuples(expr)
    if len(expr) < 2:
        result.append(expr[0][0])
        result.append(expr[0][1])
        return result

    for indx in xrange(len(expr)-1):
        # print indx, expr[indx]
        if step_plus:
            step_plus = False
            if (indx+2) == len(expr):
                result.append(expr[indx+1][0])
                result.append(expr[indx+1][1])
            continue
        if was_opened:
            # print 'was opened///'
            result.append(expr[indx][0])
            result.append(expr[indx][1])
            if (indx+2) == len(expr):
                result.append(expr[indx+1][0])
                result.append(expr[indx+1][1])
        else:
            # print 'not was opened...'
            if expr[indx+1][0] == '*' and type(expr[indx+1][1]) == list:
                # print 'next is braket with mull'
                # when you met situation a*(b*c)
                if len(expr[indx+1][1]) == 3 and expr[indx+1][1][1] == '*':
                    result.append(expr[indx][0])
                    result.append(expr[indx][1])
                    result.append(expr[indx+1][0])
                    for it in expr[indx+1][1]:
                        result.append(it)
                    step_plus = True
                    continue
                in_braket_list = set_fake_brackets(expr[indx+1][1])
                # print 'in braket list ', expr[indx+1][1], in_braket_list
                first_mul = expr[indx]
                need_external_braket = False
                if not indx and len(expr) > 2: #if it's first el in expression
                    if expr[indx+2][0] in ('*', '/'):
                        need_external_braket = True
                elif indx+2 == len(expr): #if it's last el in expression
                    if expr[indx][0] == '*':
                        result.append('*')
                        first_mul = ('+', expr[indx][1])
                        need_external_braket = True
                else:  # if it's midle el in expression
                    # print 'ELSE_________'
                    if indx+3 <= len(expr) and expr[indx+2][0] in ('*', '/'):
                        need_external_braket = True
                    if expr[indx][0] == '*':
                        result.append('*')
                        first_mul = ('+', expr[indx][1])

                tmp_res = []
                for element in convert_to_tuples(in_braket_list):
                    # print first_mul, element
                    tmp_el = mull_div(first_mul, element, expr[indx+1][0])
                    # print 'm---', element, tmp_el
                    if need_external_braket:
                        # print 'need external', 
                        for it in tmp_el:
                            tmp_res.append(it)
                    else:
                        for it in tmp_el:
                            result.append(it)

                    was_opened = True
                    step_plus = True
                # print 'prev result', result
                if tmp_res:
                    result.append(tmp_res[1:])
            elif expr[indx+1][0] in ('/', '*') and type(expr[indx][1]) == list:
                in_braket_list = set_fake_brackets(expr[indx][1])
                # print 'divdivdiv next is bratek with div'
                for element in convert_to_tuples(in_braket_list):
                    # print '..........', element, expr[indx+1]
                    tmp_el = mull_div(element, (expr[indx][0],expr[indx+1][1]), expr[indx+1][0])
                    # print 'd---', element, tmp_el
                    for it in tmp_el:
                        result.append(it)
                    was_opened = True
                    step_plus = True
                    # print 'prev result', result
            # elif exrp[indx+1][0] == '*' and type()
            else:
                result.append(expr[indx][0])
                result.append(expr[indx][1])
                if (indx+2) == len(expr):
                    result.append(expr[indx+1][0])
                    result.append(expr[indx+1][1]) 
                # print 'usual operand', result
    # print 'rrererererere', result, was_opened
    return result, was_opened



def get_expression_variations():
    global new_expr
    expr_list = analyze_expression()
    # expr = convert_to_tuples(expr_list)
    print expr_list
    result = [item for item in expr_list]
    global_res = []
    # global_res.append(expr_list)
    was_opened = True
    while was_opened:
        # print 'lll'
        result, was_opened = open_brakets(result)
        if was_opened:
            # result = set_brackets(result[1:])
            global_res.append(result[1:])
        # print 'eeeeeedede ', was_opened, result
        result = result[1:]
        # print '\n', global_res, result
    expr_variations = []
    if not global_res:
        global_res.append(result)
    # add original exrpession
    orig_expr = set_brackets(expr_list)
    tmp_expr = []
    
    for index, var in enumerate(global_res):
        tmp_var = set_fake_brackets(var)
        tmp_var = sorting(tmp_var)
        tmp_vars = permutation(tmp_var)
        for i, expr in enumerate(tmp_vars, 1):
            print 'Variant N%s' % i
            tmp_expr = []
            # print expr
            for item in expr:
                tmp_expr += item
            tmp_expr = set_brackets(tmp_expr[1:])
            print tmp_expr
            expr_variations.append(tmp_expr)
    return expr_variations, orig_expr
