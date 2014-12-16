

class MNode():

    def __init__(self, id, operation, left_op=None, right_op=None):
        self.id = id
        self.operation = operation
        self.left_op = left_op
        self.right_op = right_op

    def __repr__(self):
        return "Node %s operation: %s, left_op: %s, right_op: %s" % (self.id, self.operation, self.left_op, self.right_op)