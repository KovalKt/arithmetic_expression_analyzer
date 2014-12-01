import string
import sys

Buffer = []
open_brackets_count = 0
close_brackets_count = 0
index_counter = 0

(EXPR, VAR, AFTER_ITEM_SPACE, NUMBER, DECIMAL, 
    CLOSE_BRACKET, ERROR, END, AFTER_OPEN_BRACKET) = range(9)
NOT_FIN_STATE = (EXPR, ERROR)


def append_operand(**kwargs):
    global Buffer, index_counter
    item = kwargs['item']
    Buffer += item
    index_counter += 1

def show_error(text, item):
    append_operand(item=item)
    print text, '\n', Buffer
    print '_'*(index_counter-1)+'|'

def main_automat():
    global Buffer
    STATE = 0
    global_safe = []


    def open_bracket(**kwargs):
        global open_brackets_count, Buffer

        global_safe.append(Buffer)
        Buffer = []
        # append_operand(**kwargs)
        open_brackets_count += 1

    def close_bracket(**kwargs):
        global close_brackets_count, open_brackets_count, Buffer

        close_brackets_count += 1
        if (open_brackets_count - close_brackets_count) < 0:
            return "Wrong number of brackets"
        else:
            tmp = global_safe.pop()
            tmp.append(Buffer)
            Buffer = tmp
            # append_operand(**kwargs)


    CHAR_SMB = {EXPR: (VAR, append_operand), VAR: (VAR, append_operand), \
        NUMBER: (ERROR, "Unexpected character"), AFTER_ITEM_SPACE: (ERROR, "Unexpected character"), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (VAR, append_operand)}

    NUMERIC_SMB = {EXPR: (NUMBER, append_operand), VAR: (VAR, append_operand), \
        NUMBER: (NUMBER, append_operand), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (DECIMAL, append_operand), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (NUMBER, append_operand)}
    
    OPERATION_SMB = {EXPR: (ERROR, None), VAR: (EXPR, append_operand), \
        NUMBER: (EXPR, append_operand), AFTER_ITEM_SPACE: (EXPR, append_operand), \
        DECIMAL: (EXPR, append_operand), CLOSE_BRACKET: (EXPR, append_operand), \
        AFTER_OPEN_BRACKET: (ERROR, "Wrong character! Need operand")}

    MINUS_SMB = {EXPR: (ERROR, "Wrong character! Maybe you need brackets"), VAR: (EXPR, append_operand), \
        NUMBER: (EXPR, append_operand), AFTER_ITEM_SPACE: (EXPR, append_operand), \
        DECIMAL: (EXPR, append_operand), CLOSE_BRACKET: (EXPR, append_operand), \
        AFTER_OPEN_BRACKET: (EXPR, append_operand)}
    
    OBRACKET_SMB = {EXPR: (AFTER_OPEN_BRACKET, open_bracket), VAR: (ERROR, None), \
        NUMBER: (ERROR, None), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, None), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (AFTER_OPEN_BRACKET, open_bracket)}
    
    CBRACKET_SMB = {EXPR: (ERROR, "Expected second operand"), VAR: (CLOSE_BRACKET, close_bracket), \
        NUMBER: (CLOSE_BRACKET, close_bracket), AFTER_ITEM_SPACE: (CLOSE_BRACKET, close_bracket), \
        DECIMAL: (CLOSE_BRACKET, close_bracket), CLOSE_BRACKET: (CLOSE_BRACKET, close_bracket), \
        AFTER_OPEN_BRACKET: (ERROR, "Brackets error! Expected expression inside brackets")}
    
    DOT_SMB = {EXPR: (ERROR, "Operand can't start with '.'"), VAR: (ERROR, "Unexpected character"), \
        NUMBER: (DECIMAL, append_operand), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (ERROR, "Unexpected character")}
    
    SPACE_SMB = {EXPR: (EXPR, append_operand), VAR: (AFTER_ITEM_SPACE, append_operand), \
        NUMBER: (AFTER_ITEM_SPACE, append_operand), AFTER_ITEM_SPACE: (AFTER_ITEM_SPACE, None), \
        DECIMAL: (AFTER_ITEM_SPACE, append_operand), CLOSE_BRACKET: (CLOSE_BRACKET, None), \
        AFTER_OPEN_BRACKET: (AFTER_OPEN_BRACKET, None)}
    
    ELSE_SMB = {EXPR: (ERROR, "Unexpected character"), VAR: (ERROR, "Unexpected character"), \
        NUMBER: (ERROR, "Unexpected character"), AFTER_ITEM_SPACE: (ERROR, "Unexpected character"), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, "Unexpected character"), \
        AFTER_OPEN_BRACKET: (ERROR, "Unexpected character")}

    END_SMB = {EXPR: (ERROR, None), VAR: (END, None), \
        NUMBER: (END, None), AFTER_ITEM_SPACE: (END, None), \
        DECIMAL: (END, None), CLOSE_BRACKET: (END, None), \
        AFTER_OPEN_BRACKET: (ERROR, None)}

    TABLE = {'char': CHAR_SMB,
        'numeric':NUMERIC_SMB,
        'opp': OPERATION_SMB,
        'minus': MINUS_SMB,
        'bracket_open': OBRACKET_SMB,
        'bracket_close': CBRACKET_SMB,
        'dot': DOT_SMB,
	    'space': SPACE_SMB,
        'else': ELSE_SMB,
        'end': END_SMB,
        }
    def get_item_type(item):
        if not item:
            print "0"*100
            return 'end'
        elif item in ('+', '*', '/'):
            return 'opp'
        elif item == '-':
            return 'minus'
        elif item == '.':
            return 'dot'
        elif item in string.ascii_letters:
            return 'char'
        elif item in string.digits:
            return 'numeric'
        elif item in string.whitespace:
            return 'space'
        elif item == '(':
            return 'bracket_open'
        elif item == ')':
            return 'bracket_close'
        else:
            return 'else'
        
    exp = sys.argv[1]

    for item in exp:
        ITEM_TYPE = get_item_type(item)
        STATE, action = TABLE[ITEM_TYPE].get(STATE)
        if action:
            if hasattr(action, '__call__'):
                err_str = action(item=item)
                if err_str:
                    show_error(err_str, item)
                    STATE = ERROR
            else:
                STATE = ERROR
                show_error(action, item)
        else:
            show_error("invalyd syntax", item)
            STATE = ERROR
        if STATE == ERROR or err_str:
            break
    return STATE    

def analyze_expression():
    STATE = main_automat()
    if STATE == 0:
        print "Unfinished expression", '\n', Buffer
        print '_'*(index_counter-1)+'|'
        return "Some error"
    elif STATE in (1,2,3,4,5,7):
        if (open_brackets_count - close_brackets_count) == 0:
            # print "Expression: ", Buffer
            return Buffer
        else:
            print "Wrong number of brackets", '\n', Buffer
            print '_'*(index_counter-1)+'|'
            return "Some error"

# if __name__ == "__main__":
#     analyze_expression()
    

