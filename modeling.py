import sys
import pydot
from itertools import count
from tree_builder import get_expression_variations
from helpers_modeling import MNode

finished_list = []

time = {
    '+': 2,
    '-': 2,
    '*': 3,
    '/': 5,
}

def build_tree(expr, index):
    tree = pydot.Dot(graph_type='graph')
    c = count(0)

    def add_elements(expr, tree):
        indx = c.next()
        if len(expr) > 1:
            root = MNode(indx, operation=expr[1])
            op_node = pydot.Node(indx, label="%s (%s)"%(expr[1], indx))
            
            left_child, root.left_op = add_elements(expr[0], tree)
            right_child, root.right_op = add_elements(expr[2], tree)
            
            tree.add_node(op_node)
            tree.add_edge(pydot.Edge(op_node, left_child))
            tree.add_edge(pydot.Edge(op_node, right_child))
            return op_node, root
        else:
            node = pydot.Node(c.next(), label=expr[0])
            tree.add_node(node)
            return node, expr[0]

    core, tree_root = add_elements(expr, tree)
    tree.write_png('my_tree%s.png' % index)
    return tree_root

def is_finished(node):
    if isinstance(node, MNode):
        return node in finished_list
    else:
        return True

def get_ready_nodes(node):
    if isinstance(node, MNode):
        ready_nodes = get_ready_nodes(node.left_op)
        ready_nodes += get_ready_nodes(node.right_op)
        if is_finished(node.left_op) and is_finished(node.right_op) and not is_finished(node):
            ready_nodes.append(node)
        return ready_nodes
    else:
        return []


def model_expression(expr, index, proc_number):
    tree_root = build_tree(expr, index)
    ready_node_list = get_ready_nodes(tree_root)
    exec_time = 0
    exec_output = ''

    while ready_node_list:
        operation_map = get_operation_map(ready_node_list)
        max_time_operation = max(operation_map.iteritems(), key=lambda x: len(x[1]))
        exec_time += time[max_time_operation[0]]
        if len(max_time_operation[1]) <= proc_number:
            for index in range(len(max_time_operation[1])):
                node = max_time_operation[1][index]
                exec_output += " %(proc_n)s: %(op_index)s" % dict(
                    proc_n=index+1,
                    op_index="%(op)s(%(node_index)s)".ljust(6) % dict(
                        op=node.operation,
                        node_index=node.id
                    )
                )
                finished_list.append(node)
            for index in range(proc_number-len(max_time_operation[1])):
                exec_output += " %s: %s" % (index+len(max_time_operation[1])+1, '___'.rjust(6))
            exec_output += "\n"
        else:
            for index in range(proc_number):
                node = max_time_operation[1][index]
                exec_output += " %(proc_n)s: %(op_index)s" % dict(
                    proc_n=index+1,
                    op_index="%(op)s(%(node_index)s)".ljust(6) % dict(
                        op=node.operation,
                        node_index=node.id
                    )
                )
                finished_list.append(node)
            exec_output += "\n"
        ready_node_list = get_ready_nodes(tree_root)

    return exec_time, exec_output

def get_operation_map(node_list):
    operation_map = {}
    for node in node_list:
        if node.operation in operation_map:
            operation_map[node.operation].append(node)
        else:
            operation_map[node.operation] = [node]
    return operation_map

if __name__ == "__main__":
    expression_vars, original_expr = get_expression_variations()
    proc_number = int(sys.argv[2])

    orig_exec_time, orig_exec_output = model_expression(original_expr, 0, proc_number)
    best_exec_output = orig_exec_output
    best_exec_time = orig_exec_time
    best_expression_var = original_expr

    for i, expression_var in enumerate(expression_vars, 1):
        exec_time, exec_output = model_expression(expression_var, i, proc_number)
        
        if exec_time < best_exec_time:
            best_exec_time = exec_time
            best_exec_output = exec_output
            best_expression_var = [item for item in expression_var]

    print "---"*20
    print "Best time: ", best_exec_time
    print "Expression: ", best_expression_var
    print "Execution: ", '\n', best_exec_output







