import string
import sys

Buffer = ''
brackets_count = 0
index_counter = 0

(EXPR, VAR, AFTER_ITEM_SPACE, NUMBER, DECIMAL, 
    CLOSE_BRACKET, ERROR, END, AFTER_OPEN_BRACKET) = range(9)
NOT_FIN_STATE = (EXPR, ERROR)


def append_name(**kwargs):
    global Buffer, index_counter
    item = kwargs['item']
    Buffer += item
    index_counter += 1

def show_error(text, item):
    append_name(item=item)
    print text, '\n', Buffer
    print '_'*(index_counter-1)+'|'

def main_automat():
    global Buffer
    STATE = 0


    def open_bracket(**kwargs):
        global brackets_count

        append_name(**kwargs)
        brackets_count += 1

    def close_bracket(**kwargs):
        global brackets_count

        brackets_count -= 1
        if brackets_count < 0:
            return "Wrong number of brackets"
        else:
            append_name(**kwargs)


    CHAR_SMB = {EXPR: (VAR, append_name), VAR: (VAR, append_name), \
        NUMBER: (ERROR, "Unexpected character"), AFTER_ITEM_SPACE: (ERROR, "Unexpected character"), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (VAR, append_name)}

    NUMERIC_SMB = {EXPR: (NUMBER, append_name), VAR: (VAR, append_name), \
        NUMBER: (NUMBER, append_name), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (DECIMAL, append_name), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (NUMBER, append_name)}
    
    OPERATION_SMB = {EXPR: (ERROR, None), VAR: (EXPR, append_name), \
        NUMBER: (EXPR, append_name), AFTER_ITEM_SPACE: (EXPR, append_name), \
        DECIMAL: (EXPR, append_name), CLOSE_BRACKET: (EXPR, append_name), \
        AFTER_OPEN_BRACKET: (ERROR, "Wrong character! Need operand")}

    MINUS_SMB = {EXPR: (ERROR, "Wrong character! Maybe you need brackets"), VAR: (EXPR, append_name), \
        NUMBER: (EXPR, append_name), AFTER_ITEM_SPACE: (EXPR, append_name), \
        DECIMAL: (EXPR, append_name), CLOSE_BRACKET: (EXPR, append_name), \
        AFTER_OPEN_BRACKET: (EXPR, append_name)}
    
    OBRACKET_SMB = {EXPR: (AFTER_OPEN_BRACKET, open_bracket), VAR: (ERROR, None), \
        NUMBER: (ERROR, None), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, None), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (AFTER_OPEN_BRACKET, open_bracket)}
    
    CBRACKET_SMB = {EXPR: (ERROR, "Expected second operand"), VAR: (CLOSE_BRACKET, close_bracket), \
        NUMBER: (CLOSE_BRACKET, close_bracket), AFTER_ITEM_SPACE: (CLOSE_BRACKET, close_bracket), \
        DECIMAL: (CLOSE_BRACKET, close_bracket), CLOSE_BRACKET: (CLOSE_BRACKET, close_bracket), \
        AFTER_OPEN_BRACKET: (ERROR, "Brackets error! Expected expression inside brackets")}
    
    DOT_SMB = {EXPR: (ERROR, "Operand can't start with '.'"), VAR: (ERROR, "Unexpected character"), \
        NUMBER: (DECIMAL, append_name), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None), \
        AFTER_OPEN_BRACKET: (ERROR, "Unexpected character")}
    
    SPACE_SMB = {EXPR: (EXPR, append_name), VAR: (AFTER_ITEM_SPACE, append_name), \
        NUMBER: (AFTER_ITEM_SPACE, append_name), AFTER_ITEM_SPACE: (AFTER_ITEM_SPACE, None), \
        DECIMAL: (AFTER_ITEM_SPACE, append_name), CLOSE_BRACKET: (CLOSE_BRACKET, None), \
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


if __name__ == "__main__":
    STATE = main_automat()
    if STATE == 0:
        print "Unfinished expression", '\n', Buffer
        print '_'*(index_counter-1)+'|'
    elif STATE in (1,2,3,4,5,7):
        if brackets_count == 0:
            print "Expression: ", Buffer
        else:
            print "Wrong number of brackets", '\n', Buffer
            print '_'*(index_counter-1)+'|'
    

