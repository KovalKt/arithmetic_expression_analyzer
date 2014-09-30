import string
import sys

Buffer = ''
brackets_count = 0
index_counter = 0


def main_automat():
    global Buffer
    (EXPR, VAR, AFTER_ITEM_SPACE, NUMBER, DECIMAL, 
        CLOSE_BRACKET, ERROR, END) = range(8)
    STATE = 0

    def append_name(**kwargs):
        global Buffer, index_counter
        item = kwargs['item']
        Buffer += item
        index_counter += 1

    def append_var_value(**kwargs):
        global Buffer

        item = kwargs['item']
        Buffer += item

    def open_bracket(**kwargs):
        global brackets_count

        append_name(**kwargs)
        brackets_count += 1

    def close_bracket(**kwargs):
        global brackets_count

        append_name(**kwargs)
        brackets_count -= 1


    CHAR_SMB = {EXPR: (VAR, append_name), VAR: (VAR, append_name), \
        NUMBER: (ERROR, "Unexpected character"), AFTER_ITEM_SPACE: (ERROR, "Unexpected character"), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None)}

    NUMERIC_SMB = {EXPR: (NUMBER, append_name), VAR: (VAR, append_name), \
        NUMBER: (NUMBER, append_name), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (DECIMAL, append_name), CLOSE_BRACKET: (ERROR, None)}
    
    OPERATION_SMB = {EXPR: (ERROR, None), VAR: (EXPR, append_name), \
        NUMBER: (EXPR, append_name), AFTER_ITEM_SPACE: (EXPR, append_name), \
        DECIMAL: (EXPR, append_name), CLOSE_BRACKET: (EXPR, append_name)}
    
    OBRACKET_SMB = {EXPR: (EXPR, open_bracket), VAR: (ERROR, None), \
        NUMBER: (ERROR, None), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, None), CLOSE_BRACKET: (ERROR, None)}
    
    CBRACKET_SMB = {EXPR: (ERROR, "Expected second operand"), VAR: (CLOSE_BRACKET, close_bracket), \
        NUMBER: (CLOSE_BRACKET, close_bracket), AFTER_ITEM_SPACE: (CLOSE_BRACKET, close_bracket), \
        DECIMAL: (CLOSE_BRACKET, close_bracket), CLOSE_BRACKET: (CLOSE_BRACKET, close_bracket)}
    
    DOT_SMB = {EXPR: (ERROR, "Operand can't start with '.'"), VAR: (ERROR, "Unexpected character"), \
        NUMBER: (DECIMAL, append_name), AFTER_ITEM_SPACE: (ERROR, None), \
        DECIMAL: (ERROR, "Unexpected character"), CLOSE_BRACKET: (ERROR, None)}
    
    SPACE_SMB = {EXPR: (EXPR, append_name), VAR: (AFTER_ITEM_SPACE, append_name), \
        NUMBER: (AFTER_ITEM_SPACE, append_name), AFTER_ITEM_SPACE: (AFTER_ITEM_SPACE, None), \
        DECIMAL: (AFTER_ITEM_SPACE, append_name), CLOSE_BRACKET: (CLOSE_BRACKET, None)}
    
    ELSE_SMB = {EXPR: (ERROR, 3), VAR: (ERROR, 3), \
        NUMBER: (ERROR, 3), AFTER_ITEM_SPACE: (ERROR, 3), \
        DECIMAL: (ERROR, 3), CLOSE_BRACKET: (ERROR, 3)}

    END_SMB = {EXPR: (ERROR, None), VAR: (END, None), \
        NUMBER: (END, None), AFTER_ITEM_SPACE: (END, None), \
        DECIMAL: (END, None), CLOSE_BRACKET: (END, None)}

    TABLE = {'char': CHAR_SMB,
        'numeric':NUMERIC_SMB,
        'opp': OPERATION_SMB,
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
        elif item in ('+', '-', '*', '/'):
            return 'opp'
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
    # print "expresion: ", exp
    while not (STATE == END or STATE == ERROR):
        for item in exp:
            ITEM_TYPE = get_item_type(item)
            # print '44444', ITEM_TYPE
            STATE, action = TABLE[ITEM_TYPE].get(STATE)
            # print "state", STATE, "item type", ITEM_TYPE, "item - ", item
            if action is not None:
                if hasattr(action, '__call__'):
                    action(item=item)
                else:
                    append_name(item=item)
                    print ERROR_TABLE[action]
                    print Buffer
                    print '_'*(index_counter-1)+'|'
        if STATE != ERROR:
            STATE = END 
    return STATE    


if __name__ == "__main__":
    STATE = main_automat()

    if STATE != 6 and brackets_count == 0:
        print "Buffer:", Buffer


