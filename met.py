# Eftychia Bourli
# Open the folder with the code for compilation 
import sys

cimple = sys.argv[1]
try:
    file = open(cimple, 'rb') 
except IOError:
    print ("Could not read file:", cimple)
    exit() 


# Declaration of global variable
word_unit = ""                         # Lektiki monada  
identifier= 0                          # Anagnoristiko
line = 1                               # This shows the current line in the file

list_of_quads = []                     # for intermediate code                
number_of_temporary_variables = 0      # for intermediate code
ID = '' # Program name                 # for intermediate code
there_is_Function_or_Procedure = 0     # for c code

scopes = []                            # for symbol table
Symbol_Table = open("test.symb","w")   # for symbol table

FinalCode = open("text.asm","w")       # for final code
list_of_quads_for_final_code = []      # for final code
jump_to_main = 0                       # for final code
function_or_procedure_call = 0         # for final code

def lexical_analyst():
    global identifier
    global word_unit
    global line

    # Local variables
    word = ""  # word  == Word_unit
    state = 0  # state == Identifier

    # Declaration of states
    start = 0
    letter = 1
    digit = 2
    symbol = 3
    less = 4
    greater = 5
    colon = 6
    hashtag = 7
    reserved_word = 8
    
    OK = -2
    error = -1
    
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    reserved_words = ['program','declare','if','else','while','switchcase',
                      'forcase','incase','case','default','not','and','or',
                      'function','procedure','call','return','in','inout',
                      'input','print']
    symbols = ',+-*/=();[].}{'
    whitespace = [' ','\t','\r']
    
    while state!=OK and state!=error:
        character = file.read(1)
        character = character.decode('ascii')

        if character == "":
            identifier="" 
            state = error
            print("lexical_analyst_Error: Empty file \n")
            exit()
        elif character in alphabet:
            state = letter
            word += character
            while 1:
                next_character = file.read(1) 
                next_character = next_character.decode('ascii')
                file.seek(-1, 1) 
                if (next_character not in alphabet) and (next_character not in numbers): 
                    if len(word) > 30: 
                        word = ""
                        print("lexical_analyst_Error: Line",line,"-> Too long word \n")
                        state = error
                        exit()
                    elif word in reserved_words:
                        state = reserved_word
                        word_unit = word
                        identifier = state
                        word = ""
                        state = OK
                        break
                    else:
                        word_unit = word
                        identifier = state
                        state = start
                        word = ""
                        state = OK
                        break
                next_character = file.read(1) 
                next_character = next_character.decode('ascii')
                word += next_character
        elif character in numbers:
            state = digit
            word += character
            next_character = file.read(1) 
            next_character = next_character.decode('ascii')
            file.seek(-1, 1) 
            if (next_character not in numbers):
                if (int(word) > pow(2,32)-1 or int(word) < -(pow(2,32)-1)):
                    word = ""
                    print("lexical_analyst_Error: Line",line,"-> Too big or too small number \n")
                    state = error
                    exit()
                word_unit = word
                identifier = state
                word = ""
                state = OK
        elif character in symbols:
            state = symbol
            word_unit = character
            identifier = state
            word = ""
            state = OK
        elif character in whitespace:
            state = start
        elif character == '<':  
            state = less
            word += character
            next_character = file.read(1) 
            next_character = next_character.decode('ascii')
            if (next_character == "="):
                word += next_character
                word_unit = word
                identifier = state
                word = ""
                state = OK
            elif (next_character == ">"):
                word += next_character
                word_unit = word
                identifier = state
                word = ""
                state = OK
            else:
                file.seek(-1, 1) 
                word_unit = word
                identifier = state
                word = ""
                state = OK
        elif character == '>':
            state = greater
            word += character
            next_character = file.read(1) 
            next_character = next_character.decode('ascii')
            if (next_character == "="):
                word += next_character
                word_unit = word
                identifier = state
                word = ""
                state = OK
            else:
                file.seek(-1, 1) 
                word_unit = word
                identifier = state
                word = ""
                state = OK
        elif character == ':':
            state = colon
            word += character
            next_character = file.read(1) 
            next_character = next_character.decode('ascii')
            if (next_character == "="):
                word += next_character
                word_unit = word
                identifier = state
                word = ""
                state = OK
            else:
                print("lexical_analyst_Error: Line",line,"-> find ':' expected ':=' \n ")
                file.seek(-1, 1)
                state = error
                exit()
        elif character == "#":    
            state = hashtag
            while 1:
                next_character = file.read(1) 
                next_character = next_character.decode('ascii')
                if (next_character == "#"):
                    break
                elif (next_character == "\n"):   
                    line += 1
                elif (next_character == ""):
                    word = ""
                    print("lexical_analyst_Error: Line",line,"-> Comments do not close \n ")
                    state = error
                    exit()
        elif character == "\n":   
            line += 1
        else:
            identifier="" 
            word_unit = 0
            print("lexical_analyst_Error: Line",line,"-> Symbol `",character,"` is not valid symbol! \n")
            state = error
            exit()



def syntax_analyst():
    lexical_analyst()
    program()
    
def program():
    global identifier
    global word_unit
    global line
    global ID # intermediate code 

    if(word_unit == "program"):
        lexical_analyst()
        ID = word_unit # intermediate code
        addScope() # symbol table
        if(identifier == 1): # 1 is for alphanumeric
            lexical_analyst()
            block(ID) # intermediate code
            if (word_unit == "."):
                return
            else:
                print("syntax_analyst_Error in program: Line",line,"-> '.' not found at the end \n")  
                exit()
        else:
            print("syntax_analyst_Error in program: Line",line,"-> Program name is not valid \n")
            exit()
    else:
        print("syntax_analyst_Error in program: Line",line,"-> The program does not start with the word 'program' \n")
        exit()

def block(name):
    global word_unit
    global line
    global ID # intermediate code

    if (word_unit == "{"):
        lexical_analyst()
        declarations()
        subprograms()
        genquad("begin_block", name,"_","_")  # intermediate code
        if name != ID:
            starting_Quad = nextquad() # symbol table
            startingQuad(starting_Quad) # symbol table
        blockstatements()
        if (name == ID): # intermediate code
            genquad("halt","_","_","_") # intermediate code
        genquad("endblock", name,"_","_") # intermediate code
        if (word_unit == "}"):
            lexical_analyst()
            frameLength() # symbol table
            symbolTable() # symbol table
            final_code()  # final code
            deleteScope() # symbol table
        else:
            print("syntax_analyst_Error in block: Line",line,"-> Block did not close with '}' \n")
            exit()
    else:
        print("syntax_analyst_Error in block: Line",line,"-> Block did not open with '{' \n")
        exit()

def declarations():
    global word_unit
    global line
    
    while (word_unit == "declare"):
        lexical_analyst()
        varlist()
        if (word_unit == ';'):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in declaretions: Line",line,"-> Declarations did not end with ';' \n")
            exit()  

def varlist():
    global identifier
    global word_unit
    global line

    if (identifier == 1): # 1 is for alphanumeric
        addEntity(word_unit, "Variable", None) # symbol table
        lexical_analyst()
        while (word_unit == ","):
            lexical_analyst()
            if (identifier == 1):
                addEntity(word_unit, "Variable", None) # symbol table
                lexical_analyst()
            else:
                print("syntax_analyst_Error in varlist: Line",line,"-> expected id after ',' \n")
                exit()
    else:
        print("syntax_analyst_Error in varlist: Line",line,"-> is not a valid id! \n")
        exit()

def subprograms():
    global word_unit
    global there_is_Function_or_Procedure

    while (word_unit == "function" or word_unit == "procedure"):
        there_is_Function_or_Procedure = 1
        subprogram()

def subprogram():
    global identifier
    global word_unit
    global line

    if (word_unit == "function"):
        lexical_analyst() 
        if (identifier == 1):
            name = word_unit # intermediate code
            addEntity(name, "Function", None) # symbol table
            addScope() # symbol table
            lexical_analyst()
            if (word_unit == "("):
                lexical_analyst()
                formalparlist()
                if (word_unit == ")"):
                    lexical_analyst()
                    block(name)
                else:
                    print("syntax_analyst_Error in subprogram: Line",line,"-> expected ')' after formalparlist \n")
                    exit() 
            else:
                print("syntax_analyst_Error in subprogram: Line",line,"-> expected '(' after ID of function \n")
                exit()
        else:
            print("syntax_analyst_Error in subprogram: Line",line,"-> is not a valid id! \n")
            exit()
    else:
        lexical_analyst() 
        if (identifier == 1):
            name = word_unit # intermediate code
            addEntity(name, "Procedure", None) # symbol table
            addScope() # symbol table
            lexical_analyst()
            if (word_unit == "("):
                lexical_analyst()
                formalparlist()
                if (word_unit == ")"):
                    lexical_analyst()
                    block(name)
                else:
                    print("syntax_analyst_Error in subprogram: Line",line,"-> expected ')' after formalparlist \n")
                    exit() 
            else:
                print("syntax_analyst_Error in subprogram: Line",line,"-> expected '(' after ID of procedure \n")
                exit()
        else:
            print("syntax_analyst_Error in subprogram: Line",line,"-> is not a valid id! \n")
            exit()

def formalparlist():
    global word_unit

    formalparitem()
    while (word_unit == ","):
        lexical_analyst()
        formalparitem()

def formalparitem():
    global identifier
    global word_unit
    global line

    if (word_unit == "in"):
        addFormalParameter("in") # symbol table
        lexical_analyst()
        if (identifier == 1): # 1 is for alphanumeric
            addEntity(word_unit, "Parameter", "in") # symbol table
            lexical_analyst()
        else:
            print("syntax_analyst_Error in formalparitem: Line",line,"-> is not a valid id! \n")
            exit()
    elif (word_unit == "inout"):
        addFormalParameter("in") # symbol table
        lexical_analyst()
        if (identifier == 1): # 1 is for alphanumeric
            addEntity(word_unit, "Parameter", "inout") # symbol table
            lexical_analyst()
        else:
            print("syntax_analyst_Error in formalparitem: Line",line,"-> is not a valid id! \n")
            exit()
    else:
        print("syntax_analyst_Error in formalparitem: Line",line,"-> expected 'in' or 'inout' \n")
        exit()

def statements():
    global word_unit
    global line
    
    if (word_unit == "{"):
        lexical_analyst()
        statement()
        while (word_unit == ";"):
            lexical_analyst()
            statement()
        if (word_unit == "}"):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in statements: Line",line,"-> opened with '{' for statements and did not close with '}' ,I got" , word_unit ,"  \n")
            exit()
    else:
        statement()
        if (word_unit == ";"):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in statements: Line",line,"-> expected ';' after statement \n")
            exit()

def blockstatements():
    global word_unit

    statement()
    while (word_unit == ";"):
        lexical_analyst()
        statement()

def statement():
    global identifier
    global word_unit

    if (identifier == 1):
        id = word_unit # intermediate code
        searchEntity(id, "Variable") # semantic analyst
        lexical_analyst() # intermediate code
        assignStat(id) # intermediate code
    elif (word_unit == "if"):
        lexical_analyst()
        ifStat()
    elif (word_unit == "while"):
        lexical_analyst()
        whileStat()
    elif (word_unit == "switchcase"):
        lexical_analyst()
        switchcaseStat()
    elif (word_unit == "forcase"):
        lexical_analyst()
        forcaseStat()
    elif (word_unit == "incase"):
        lexical_analyst()
        incaseStat()
    elif (word_unit == "call"):
        lexical_analyst()
        callStat()
    elif (word_unit == "return"):
        lexical_analyst()
        returnStat()
    elif (word_unit == "input"):
        lexical_analyst()
        inputStat()
    elif (word_unit == "print"):
        lexical_analyst()
        printStat()

def assignStat(id):
    global word_unit

    if (word_unit == ":="):
        lexical_analyst()
        E_place = expression() # intermediate code
        genquad(":=",E_place,"_",id) # intermediate code
    else:
        print("syntax_analyst_Error in assignStat: Line",line,"-> expected ':=' after ID \n")
        exit()

def ifStat(): 
    global word_unit
    global line

    if (word_unit == "("):
        lexical_analyst()
        B = condition() # intermediate code
        B_true = B[0] # intermediate code   
        B_false = B[1] # intermediate code
        if (word_unit == ")"):
            lexical_analyst()
            backpatch(B_true,nextquad()) # intermediate code
            statements()
        else:
            print("syntax_analyst_Error in ifStat: Line",line,"-> expected ')' but got", word_unit," after condition \n")
            exit()
        elsepart(B_false) # intermediate code 
    else:
        print("syntax_analyst_Error in ifStat: Line",line,"-> expected '(' after 'if' \n")
        exit()

def elsepart(B_false): # intermediate code
    global word_unit

    if (word_unit == "else"):
        lexical_analyst()
        ifList = makelist(nextquad()) # intermediate code
        genquad("jump","_","_","_") # intermediate code
        backpatch(B_false,nextquad()) # intermediate code
        statements()
        backpatch(ifList,nextquad ()) # intermediate code
    else: # intermediate code
        backpatch(B_false,nextquad ()) # intermediate code

def whileStat():
    global word_unit
    global line

    if (word_unit == "("):
        lexical_analyst()
        Bquad = nextquad() # intermediate code
        B = condition() # intermediate code
        B_true = B[0] # intermediate code
        B_false = B[1] # intermediate code
        backpatch(B_true,nextquad()) # intermediate code
        if (word_unit == ")"):
            lexical_analyst()
            statements()
            genquad("jump","_","_",Bquad) # intermediate code
            backpatch(B_false,nextquad()) # intermediate code
        else:
            print("syntax_analyst_Error in whileStat: Line",line,"-> expected ')' after condition \n")
            exit()
    else:
        print("syntax_analyst_Error in whileStat: Line",line,"-> expected '(' after 'if' \n")
        exit()

def switchcaseStat():
    global word_unit
    global line
    
    exitlist = emptylist() # intermediate code
    while ( word_unit == "case"):
        lexical_analyst()
        if ( word_unit == "("):
            lexical_analyst()
            cond = condition() # intermediate code
            cond_True = cond[0] # intermediate code
            cond_False = cond[1] # intermediate code
            backpatch(cond_True, nextquad()) # intermediate code
            if ( word_unit == ")"):
                lexical_analyst()
                statements()
                e = makelist(nextquad()) # intermediate code
                genquad("jump","_","_","_") # intermediate code
                exitlist = merge(exitlist, e) # intermediate code
                backpatch(cond_False,nextquad()) # intermediate code
            else:
                print("syntax_analyst_Error in switchStat: Line",line,"-> expected ')' after condition \n")
                exit()
        else:
            print("syntax_analyst_Error in switchStat: Line",line,"-> expected '(' after case \n")
            exit()
    if (word_unit == "default"):
        lexical_analyst()
        statements()
        backpatch(exitlist,nextquad()) # intermediate code
    else: 
        print("syntax_analyst_Error in switchStat: Line",line,"-> expected 'default'  \n")
        exit()

def forcaseStat():  
    global word_unit
    global line
    
    sQuad = nextquad() # intermediate code
    while ( word_unit == "case"):
        lexical_analyst()
        if ( word_unit == "("):
            lexical_analyst()
            cond = condition() # intermediate code
            cond_true = cond[0] # intermediate code
            cond_false = cond[1] # intermediate code
            backpatch(cond_true, nextquad()) # intermediate code
            if ( word_unit == ")"):
                lexical_analyst()
                statements()
                genquad("jump","_","_",sQuad) # intermediate code
                backpatch(cond_false,nextquad()) # intermediate code
            else:
                print("syntax_analyst_Error in forcaseStat: Line",line,"-> expected ')' after condition \n")
                exit()
        else:
            print("syntax_analyst_Error in forcaseStat: Line",line,"-> expected '(' after case \n")
            exit()
    if (word_unit == "default"):
        lexical_analyst()
        statements()
    else: 
        print("syntax_analyst_Error in forcaseStat: Line",line,"-> expected 'default'  \n")
        exit()

def incaseStat():
    global word_unit
    global line
    
    t = newtemp() # intermediate code
    first_quad = nextquad() # intermediate code
    genquad(":=","0","_",t) # intermediate code
    while ( word_unit == "case"):
        lexical_analyst()
        if ( word_unit == "("):
            lexical_analyst()
            cond = condition() # intermediate code
            cond_true = cond[0] # intermediate code
            cond_false = cond[1] # intermediate code
            backpatch(cond_true,nextquad()) # intermediate code
            if ( word_unit == ")"):
                lexical_analyst()
                statements()
                genquad(":=","1","_",t) # intermediate code
                backpatch(cond_false,nextquad()) # intermediate code
            else:
                print("syntax_analyst_Error in incaseStat: Line",line,"-> expected ')' after condition \n")
                exit()
        else:
            print("syntax_analyst_Error in incaseStat: Line",line,"-> expected '(' after case \n")
            exit()
    genquad("=","1",t,first_quad) # intermediate code

def returnStat():
    global word_unit
    global line

    if ( word_unit == "("):
        lexical_analyst()
        E_place = expression() # intermediate code
        genquad("retv", E_place, "_","_") # intermediate code
        if ( word_unit == ")"):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in returnStat: Line",line,"-> expected ')' after expression \n")
            exit()
    else:
        print("syntax_analyst_Error in returnStat: Line",line,"-> expected '(' after return \n")
        exit()
    return E_place # intermediate code

def callStat():
    global identifier
    global word_unit
    global line

    if ( identifier == 1):
        assign_v = word_unit # intermediate code
        lexical_analyst()
        if ( word_unit == "("):
            lexical_analyst()
            actualparlist() 
            genquad("call",assign_v,"_","_") # intermediate code
            if ( word_unit == ")"):
                lexical_analyst()
            else:
                print("syntax_analyst_Error in callStat: Line",line,"-> expected ')' after actualparlist \n")
                exit()
        else:
            print("syntax_analyst_Error in callStat: Line",line,"-> expected '(' after ID \n")
            exit()
    else:
        print("syntax_analyst_Error in callStat: Line",line,"-> is not a valid id! \n")
        exit()

def printStat():
    global word_unit
    global line

    if ( word_unit == "("):
        lexical_analyst()
        E_place = expression() # intermediate code
        genquad("out", E_place,"_","_") # intermediate code
        if ( word_unit == ")"):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in printStat: Line",line,"-> expected ')' after expression \n")
            exit()
    else:
        print("syntax_analyst_Error in printStat: Line",line,"-> expected '(' after print \n")
        exit()

def inputStat():
    global identifier
    global word_unit
    global line

    if ( word_unit == "("):
        lexical_analyst()
        if (identifier == 1):
            id_place = word_unit # intermediate code
            genquad("inp", id_place, "_","_") # intermediate code
            searchEntity(id_place, "Variable") # semantic analyst
            lexical_analyst()
            if ( word_unit == ")"):
                lexical_analyst()
            else:
                print("syntax_analyst_Error in inputStat: Line",line,"-> expected ')' after expression \n")
                exit()
        else:
            print("syntax_analyst_Error in inputStat: Line",line,"-> is not a valid id! \n")
            exit()
    else:
        print("syntax_analyst_Error in inputStat: Line",line,"-> expected '(' after return \n")
        exit()
    
def actualparlist(): 
    global word_unit
    actualparlist_ = [] # intermediate code
    actualparitem_ = actualparitem() # intermediate code
    actualparlist_.append(actualparitem_) # intermediate code
    while ( word_unit == ","):
        lexical_analyst()
        actualparitem_ = actualparitem() # intermediate code
        actualparlist_.append(actualparitem_) # intermediate code
    for actualparitem_ in actualparlist_: # intermediate code
       genquad("par",actualparitem_[0],actualparitem_[1],"_") # intermediate code 

def actualparitem():   
    global identifier
    global word_unit
    global line

    if (word_unit == "in"):
        lexical_analyst()
        expression_ = expression() # intermediate code
        return [expression_,"CV"] # intermediate code
    elif ( word_unit == "inout"):
        lexical_analyst()
        if (identifier == 1):
            id = word_unit # intermediate code 
            searchEntity(id, "Variable") # semantic analyst
            lexical_analyst()
            return [id,"REF"] # intermediate code
        else:
            print("syntax_analyst_Error in actualparitem: Line",line,"-> is not a valid id! \n")
            exit()
    else:
        print("syntax_analyst_Error in actualparitem: Line",line,"-> expected 'in' or 'inout'  \n")
        exit()

def condition():
    global word_unit

    Q1 = boolterm() # intermediate code
    B_true = Q1[0] # intermediate code
    B_false = Q1[1] # intermediate code
    while(word_unit == "or"):
        lexical_analyst()
        backpatch(B_false, nextquad()) # intermediate code
        Q2 = boolterm() # intermediate code
        B_true = merge(B_true, Q2[0]) # intermediate code
        B_false = Q2[1] # intermediate code
    return [B_true, B_false] # intermediate code

def boolterm():
    global word_unit

    R1 = boolfactor() # intermediate code
    Q_true = R1[0] # intermediate code
    Q_false = R1[1] # intermediate code
    while(word_unit == "and"):
        lexical_analyst()
        backpatch(Q_true, nextquad()) # intermediate code
        R2 = boolfactor() # intermediate code
        Q_false = merge(Q_false, R2[1]) # intermediate code
        Q_true = R2[0] # intermediate code
    return [Q_true, Q_false] # intermediate code

def boolfactor():
    global identifier
    global word_unit
    global line

    if ( word_unit == "not"):
        lexical_analyst()
        if (word_unit == "["):
            lexical_analyst()
            B = condition() # intermediate code
            R_true = B[0] # intermediate code
            R_false = B[1] # intermediate code
            if (word_unit == "]"):
                lexical_analyst()
            else:
                print("syntax_analyst_Error in boolfactor: Line",line,"-> expected ']' after condition \n")
                exit()
            return [R_false, R_true] # intermediate code
        else:
            print("syntax_analyst_Error in boolfactor: Line",line,"-> expected '[' after not \n")
            exit()
    elif ( word_unit == "["):
        lexical_analyst()
        B = condition() # intermediate code
        R_true = B[0] # intermediate code
        R_false = B[1] # intermediate code
        if (word_unit == "]"):
            lexical_analyst()
        else:
            print("syntax_analyst_Error in boolfactor: Line",line,"-> expected ']' after condition \n")
            exit()
        return [R_true, R_false] # intermediate code 
    else:
        E1_place = expression() # intermediate code
        if ( identifier == 4 or identifier == 5 or word_unit == "="): # 4 is for <,<=,<> and 5 is for >,>=
            relop = word_unit # intermediate code
            lexical_analyst() # intermediate cod
            E2_place = expression() # intermediate code
            R_true = makelist(nextquad()) # intermediate code
            genquad(relop, E1_place, E2_place, "_") # intermediate code
            R_false = makelist(nextquad()) # intermediate code
            genquad("jump","_","_","_") # intermediate code
            return [R_true, R_false] # intermediate code
    
def expression():
    global word_unit
    
    optional_Sign =optionalSign() # intermediate code
    T1_place = optional_Sign + str(term()) # intermediate code
    while (word_unit == "+" or word_unit == "-"):
        op = word_unit # intermediate code
        lexical_analyst()
        T2_place = str(term()) # intermediate code
        w = newtemp() # intermediate code
        genquad(op, T1_place, T2_place, w) # intermediate code
        T1_place = w # intermediate code
    E_place = T1_place # intermediate code
    return E_place # intermediate code

def term():
    global word_unit

    F1_place = factor() # intermediate code
    while (word_unit == "*" or word_unit == "/"):
        op = word_unit # intermediate code
        lexical_analyst()
        F2_place = factor() # intermediate code
        w = newtemp() # intermediate code
        genquad(op, F1_place, F2_place, w) # intermediate code
        F1_place = w # intermediate code
    T_place = F1_place # intermediate code
    return T_place # intermediate code

def factor():
    global identifier
    global word_unit
    global line

    F_place = "" # intermediate code
    if ( identifier == 2): # 2 is for Integer
        F_place = word_unit # intermediate code
        lexical_analyst()
    elif ( word_unit == "("):
        lexical_analyst()
        E_place = expression() # intermediate code
        if ( word_unit == ")"):
            lexical_analyst()
            F_place = E_place # intermediate code
        else:
            print("syntax_analyst_Error in factor: Line",line,"-> expected ')' after expression \n")
            exit()
    elif ( identifier == 1):
        id_place = word_unit # intermediate code
        lexical_analyst()
        id_tail = idtail(id_place) # intermediate code
        if ( id_tail == "ID"): # intermediate code
            F_place = id_place # intermediate code
            searchEntity(id_place, "Variable") # semantic analyst
        else: # intermediate code
            F_place = id_tail # intermediate code
            searchEntity(id_place, "Function") # semantic analyst
    else:
        print("syntax_analyst_Error in factor: Line",line,"-> expected variable or expression and got ",word_unit," \n")
        exit()
    return F_place

def idtail(assign_v):
    global word_unit
    global line

    if (word_unit == "("):    
        lexical_analyst()
        actualpar_list = actualparlist() # intermediate code
        if ( word_unit == ")"):
            lexical_analyst()
            E_place = newtemp() # intermediate code
            genquad("par",E_place,"RET","_") # intermediate code
            genquad("call",assign_v,"_","_") # intermediate code
            return E_place
        else:
            print("syntax_analyst_Error in idtail: Line",line,"-> expected ')' after actualparlist \n")
            exit()
    else: # intermediate code
        return "ID" # intermediate code

def optionalSign():
    global word_unit

    if (word_unit == "+" or word_unit == "-"):
        optional_Sign = word_unit # intermediate code
        lexical_analyst()
        return optional_Sign # intermediate code
    else: # intermediate code
        return "" # intermediate code



# Auxiliary subroutines for Intermediate Code #########################################################

# nextquad(): Returns the number of the next quad to be provided
def nextquad():
    global list_of_quads

    id_of_quad = str(len(list_of_quads)+1) 
    return id_of_quad

# genquad(): Creates the next quad (op, x, y, z)
def genquad(op,x,y,z):
    global list_of_quads
    global list_of_quads_for_final_code # final code
    new_quad = [nextquad(),[op,x,y,z]]
    list_of_quads.append(new_quad)
    list_of_quads_for_final_code.append(new_quad) # for final code
    return

# newtemp(): Creates and returns a new temporary variable of the form: T_0, T_1, T_2 ...
def newtemp():
    global number_of_temporary_variables

    new_temporary_variable = 'T_'+ str(number_of_temporary_variables)
    number_of_temporary_variables += 1
    addEntity(new_temporary_variable,"TemporaryVariable", None) # symbol table
    return new_temporary_variable

# emptylist(): Creates a blank list of quad tags
def emptylist():
    empty_list = []
    return empty_list

# makelist(): Creates a list of quad tags that contains only x
def makelist(x):
    new_list = [x]     
    return new_list

# merge(list_1, list_2): Creates a list of quad tags by merging list_1 and list_2
def merge(list_1, list_2):
    merge_lists = []
    merge_lists.extend(list_1)
    merge_lists.extend(list_2)
    return merge_lists

# backpatch(list, z): Adds the 'z' label to each quad in the list
def backpatch(list, z):
    global list_of_quads

    for j in list:          
        for i in list_of_quads:
            if j == i[0]:
                i[1][3] = z
                break

def intermediate_code():
    global list_of_quads

    file_int_code = open("test.int","w")
    if list_of_quads != []:
        for i in list_of_quads:
            file_int_code.write(str(i[0])+": "+str(i[1][0])+", "+str(i[1][1])+", "+str(i[1][2])+", "+str(i[1][3])+"\n")
        file_int_code.close()    

def c_code():
    global there_is_Function_or_Procedure
    mains_code = []
    declaration_of_variables = []
    number_of_L_tag = 1
    
    if there_is_Function_or_Procedure == 0:
        file_int_code = open("test.int","r")
        for line in file_int_code:
            line = line.replace(",","")
            line = line.replace("\n","")
            word = line.split(" ")
            #print("word"+" "+word[0]+" "+word[1]+" "+word[2]+" "+word[3]+" "+word[4])
            if word[1] == "begin_block":
                mains_code.append("L_"+str(number_of_L_tag)+":\n")
                number_of_L_tag += 1
            elif word[1] == ":=":
                mains_code.append("L_"+str(number_of_L_tag)+": "+str(word[4])+" = "+str(word[2])+"; \n")
                declaration_of_variables.append(word[4])
                number_of_L_tag += 1
            elif word[1] == "+":
                mains_code.append("L_"+str(number_of_L_tag)+": "+str(word[4])+" = "+str(word[2])+" + "+str(word[3])+"; \n")
                declaration_of_variables.append(word[4])
                number_of_L_tag += 1
            elif word[1] == "-":
                mains_code.append("L_"+str(number_of_L_tag)+": "+str(word[4])+" = "+str(word[2])+" - "+str(word[3])+"; \n")
                declaration_of_variables.append(word[4])
                number_of_L_tag += 1
            elif word[1] == "*":
                mains_code.append("L_"+str(number_of_L_tag)+": "+str(word[4])+" = "+str(word[2])+" * "+str(word[3])+"; \n")
                declaration_of_variables.append(word[4])
                number_of_L_tag += 1
            elif word[1] == "/":
                mains_code.append("L_"+str(number_of_L_tag)+": "+str(word[4])+" = "+str(word[2])+" / "+str(word[3])+"; \n")
                declaration_of_variables.append(word[4])
                number_of_L_tag += 1
            elif word[1] == "=":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" == "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == "<>":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" != "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == ">":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" > "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == ">=":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" >= "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == "<":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" < "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == "<=":
                mains_code.append("L_"+str(number_of_L_tag)+": if("+str(word[2])+" <= "+str(word[3])+") goto L_"+word[4]+"; \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == "jump":
                mains_code.append("L_"+str(number_of_L_tag)+": goto L_"+word[4]+"; \n")
                number_of_L_tag += 1
            elif word[1] == "inp":
                mains_code.append("L_"+str(number_of_L_tag)+": scanf(\"%d\", &"+word[2]+"); \n")
                declaration_of_variables.append(word[2])
                number_of_L_tag += 1
            elif word[1] == "out":
                mains_code.append("L_"+str(number_of_L_tag)+": printf(\""+str(word[2])+" =  %d\", "+word[2]+"); \n")
                number_of_L_tag += 1
            elif word[1] == "halt":
                mains_code.append("L_"+str(number_of_L_tag)+": {} \n")
                number_of_L_tag += 1
        declaration_of_variables = list(dict.fromkeys(declaration_of_variables))
        file_int_code.close()
    
        file_c_code = open("test.c","w")
        file_c_code.write("#include <stdio.h> \n \n")
        file_c_code.write("int main() \n") 
        file_c_code.write("{ \n")
        
        if declaration_of_variables != []:
            file_c_code.write("\tint ")
            for variable in range(len(declaration_of_variables)):
                if (variable+1) != len(declaration_of_variables):
                    file_c_code.write(declaration_of_variables[variable]+", ")
                else:
                    file_c_code.write(declaration_of_variables[variable]+"; \n")
       
        if mains_code != []:
            for line in mains_code:
                file_c_code.write("\t"+str(line))
        file_c_code.write("} \n")

        file_c_code.close()


# Classes for Symbol Table #########################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Scope():
    def __init__(self, level):
        self.level = level
        self.entities = []
        self.offset = 12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Entity(Scope):
    def __init__(self, name):
        self.name = name
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Variable(Entity):
    def __init__(self, name, offset):
        self.name = name
        self.type = "Variable"
        self.datatype = "Integer"
        self.offset = offset

class FormalParameter(Entity):
    def __init__(self, mode):
        self.type = "FormalParameter"
        self.datatype = "Integer"
        self.mode = mode

class Procedure(Entity):
    def __init__(self, name, startingQuad, frameLength):
        self.name = name
        self.type = "Procedure"
        self.startingQuad = startingQuad
        self.frameLength = frameLength
        self.formalParameters = []
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TemporaryVariable(Variable):
    def __init__(self,name, offset):
        self.name = name
        self.offset = offset
        self.type = "TemporaryVariable"
        self.datatype = "Integer"
        
class Parameter(Variable, FormalParameter):
    def __init__(self, name, mode, offset):
        self.name = name
        self.offset = offset
        self.type = "Parameter"
        self.datatype = "Integer"
        self.mode = mode
        
class Function(Procedure):
    def __init__(self, name, startingQuad, frameLength):
        self.name = name
        self.startingQuad = startingQuad
        self.frameLength = frameLength
        self.type = "Function"
        self.formalParameters = []
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The basic functions for Symbol Table #########################################################
def addScope():
    global scopes
    
    new_scope = Scope(len(scopes))
    scopes.append(new_scope)

def deleteScope():  
    global scopes
    
    scopes.pop()

def addEntity(entity_name, entity_type, entity_mode):
    global scopes

    if entity_type == "Variable":
        new_entity = Variable(entity_name, scopes[-1].offset)
    elif entity_type == "TemporaryVariable":
        new_entity = TemporaryVariable(entity_name, scopes[-1].offset)
    elif entity_type == "Procedure":
        new_entity = Procedure(entity_name,0,0)
    elif entity_type == "Function":
        new_entity = Function(entity_name,0,0)
    elif entity_type == "Parameter":
        new_entity = Parameter(entity_name, entity_mode, scopes[-1].offset)
    else:
        print("No type", entity_name,",",entity_type,"\n")
    
    scopes[-1].entities.append(new_entity)
    if entity_type != "Function" and entity_type != "Procedure":
        scopes[-1].offset = scopes[-1].offset + 4

# update fields
def startingQuad(startingQuad):
    global scopes

    if len(scopes[-1].entities) > 0:
        scopes[len(scopes)-2].entities[-1].startingQuad = startingQuad

# update fields
def frameLength():
    global scopes

    framelength = 12
    for entity in scopes[-1].entities:
        if entity.type != "Procedure" or entity.type != "Function":
            framelength +=4
    if len(scopes) > 1:
        scopes[-2].entities[-1].frameLength = framelength 
        
def addFormalParameter(mode):
    global scopes

    new_FormalParameter = FormalParameter(mode)
    if len(scopes)>1:  
        scopes[-2].entities[-1].formalParameters.append(new_FormalParameter)

    
def searchEntity(name, type): 
    global scopes
    global line

    for scope in reversed(scopes):
        for entity in scope.entities:
            if name == entity.name:
                if type == "Variable":
                    if entity.type == "Variable" or entity.type == "Parameter" or entity.type == "TemporaryParameter":
                        return entity
                elif type == "Procedure" :
                    if entity.type == "Procedure":
                            return entity
                elif type == "Function" :
                    if entity.type == "Function":
                            return entity
    print("Semantic analyst error from searchEntity: Line ",line,"-> Entity [name:",name,", type:",type,"] not found! \n") 
    exit()          

def symbolTable(): 
    global Symbol_Table
    global scopes

    
    scope = scopes[-1]
    Symbol_Table.write("Scope: "+str(scope.level)+"\n")
    Symbol_Table.write("Entities: \n")
    for entity in scope.entities:
        if entity.type == "Variable" or entity.type == "TemporaryVariable" :
            Symbol_Table.write("["+str(entity.type)+", name: "+str(entity.name)+", datatype: Integer, offset: "+str(entity.offset)+"] \n")
        elif entity.type == "Procedure" or entity.type == "Function":
            Symbol_Table.write("["+str(entity.type)+", name: "+str(entity.name)+", startingQuad: "+str(entity.startingQuad)+", framelength: "+str(entity.frameLength)+"] \n")
            Symbol_Table.write("Formal parameters modes : ")
            if len(entity.formalParameters) != 0:
                for formalparameter in entity.formalParameters:
                    Symbol_Table.write(str(formalparameter.mode) +" ")
            else:
                Symbol_Table.write(" no parameters")
            Symbol_Table.write("\n")
        elif entity.type == "Parameter":
            Symbol_Table.write("["+str(entity.type)+", name: "+str(entity.name)+", datatype: "+str(entity.datatype)+", mode: "+str(entity.mode)+", offset: "+str(entity.offset)+"] \n")
    Symbol_Table.write("\n")


# Auxiliary functions for Final Code #########################################################

# find and return variable v 
def findVariable(v):
    global scopes

    nestingLevel = len(scopes)
    for scope in reversed(scopes):
        nestingLevel -= 1
        for entity in scope.entities:
            if v == entity.name:
                return [entity, nestingLevel]
    

# gnlvcode(v): give access to variables or addresses stored in an activation document
# different from the function currently being translated
def gnlvcode(v):
    global scopes

    produce("lw  t0, -8(sp)")
    entity = findVariable(v)
    nestinglevel = entity[1]
    while nestinglevel > 0:
        produce("lw  t0, -8(t0)")
        nestinglevel -= 1
    produce("addi t0, t0, -"+str(entity[0].offset))

# load(v, reg): reads a variable stored in memory and transfers it to a registrar
def loadvr(v, reg):
    global scopes

    if v.lstrip("-").isdigit():
        produce("   li "+str(reg)+", "+str(v))
    else:
        entity = findVariable(v)
        if entity[1] == 0 and len(scopes) != 1: # entity[1] = nestinglevel/scope of v
            produce("   lw "+str(reg)+", -"+str(entity[0].offset)+"(gp)")
        elif entity[1] == len(scopes)-1:
            if entity[0].type == "Variable" or entity[0].type == "TemporaryVariable":
                produce("   lw "+str(reg)+", -"+str(entity[0].offset)+"(sp)")
            elif entity[0].type == "Parameter":
                if entity[0].mode == "in":
                    produce("   lw "+str(reg)+", -"+str(entity[0].offset)+"(sp)")
                elif entity[0].mode == "inout":
                    produce("   lw t0, -"+str(entity[0].offset)+"(sp)")
                    produce("   lw "+str(reg)+", (t0)")
        elif entity[1] < len(scopes)-1:   
            if entity[0].type == "Variable":
                gnlvcode(v)
                produce("   lw "+str(reg)+", (t0)")
            elif entity[0].type == "Parameter":
                if entity[0].mode == "in":
                    gnlvcode(v)
                    produce("   lw "+str(reg)+", (t0)")
                elif entity[0].mode == "inout":
                    gnlvcode(v)
                    produce("   lw t0, (t0)")
                    produce("   lw "+str(reg)+", (t0)")

# store(reg, v): stores in memory the value of a variable located in a register.
def storerv(reg, v):
    global scopes
    
    entity = findVariable(v)
    if entity[1] == 0 and len(scopes) != 1: # entity[1] = nestinglevel/scope of v
        produce("   sw "+str(reg)+", -"+str(entity[0].offset)+"(gp)")
    elif entity[1] == len(scopes)-1:
        if entity[0].type == "Variable" or entity[0].type == "TemporaryVariable":
            produce("   sw "+str(reg)+", -"+str(entity[0].offset)+"(sp)")
        elif entity[0].type == "Parameter":
            if entity[0].mode == "in":
                produce("   sw "+str(reg)+", -"+str(entity[0].offset)+"(sp)")
            elif entity[0].mode == "inout":
                produce("   lw t0, -"+str(entity[0].offset)+"(sp)")
                produce("   sw "+str(reg)+", (t0)")
    elif entity[1] < len(scopes)-1:   
        if entity[0].type == "Variable":
            gnlvcode(v)
            produce("   sw "+str(reg)+", (t0)")
        elif entity[0].type == "Parameter":
            if entity[0].mode == "in":
                gnlvcode(v)
                produce("   sw "+str(reg)+", (t0)")
            elif entity[0].mode == "inout":
                gnlvcode(v)
                produce("   lw t0, (t0)")
                produce("   sw "+str(reg)+", (t0)")
    
# like genquad, generate new line in test.asm
def produce(string): 
    global FinalCode

    FinalCode.write(string + "\n")

def final_code():
    global scopes
    global ID
    global list_of_quads_for_final_code
    global FinalCode
    global jump_to_main
    global function_or_procedure_call

    if jump_to_main == 0:
        produce("   .data")
        produce("str_ln: .asciz '\\n'")
        produce("   .text")
        produce("")
        produce("L0: ")
        produce("   j Lmain")
        jump_to_main = 1

    for quad in list_of_quads_for_final_code: 
        produce("L"+str(quad[0]+": "))
        if quad[1][0] == "begin_block":
            if quad[1][1] != ID:
                produce("   sw ra, -0(sp)")
            else:
                produce("Lmain: ")
                produce("    addi sp, sp, "+ str(scopes[0].offset))
                produce("    move gp, sp")
        elif quad[1][0] == "jump":
            produce("    j L"+str(quad[1][3])) 
        elif quad[1][0] == ":=":
            loadvr(quad[1][1], "t1")
            storerv("t1", quad[1][3])
        elif quad[1][0] == "+":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   add t1, t1, t2")
            storerv("t1", quad[1][3])
        elif quad[1][0] == "-":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   sub t1, t1, t2")
            storerv("t1", quad[1][3])
        elif quad[1][0] == "*":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   mul t1, t1, t2")
            storerv("t1", quad[1][3])
        elif quad[1][0] == "/":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   div t1, t1, t2")
            storerv("t1", quad[1][3])
        elif quad[1][0] == "<":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   blt, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == "<=":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   ble, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == ">":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   bgt, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == ">=":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   bge, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == "<>":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   bne, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == "=":
            loadvr(quad[1][1], "t1")
            loadvr(quad[1][2], "t2")
            produce("   beq, t1, t2, "+str(quad[1][3]))
        elif quad[1][0] == "inp":
            produce("   li a7, 5")
            produce("   ecall")
            produce("   mv t1, a0")
            storerv("t1", quad[1][1])
        elif quad[1][0] == "out":
            loadvr(quad[1][1], "t1")
            produce("   mv a0, t1")
            produce("   li a7, 1")
            produce("   ecall")
            produce("   la a0, str_ln")
            produce("   li a7, 4")
            produce("   ecall")
        elif quad[1][0] == "retv":
            loadvr(quad[1][1], "t1")
            produce("   lw t0, -8(sp)")
            produce("   sw t1, (t0)")
        elif quad[1][0] == "par" or quad[1][0] == "call":
            if function_or_procedure_call == 0:
                function_or_procedure_call = 1
                for q in list_of_quads_for_final_code:
                    if q[1][0] == "call":
                        func_proc_entity = findVariable(q[1][1])
                        break
                produce("   addi fp, sp, "+str(func_proc_entity[0].frameLength))
            if quad[1][2] == "CV":
                entity = findVariable(quad[1][1])
                loadvr(quad[1][1], "t1")
                if entity[0].type == "Variable" or entity[0].type == "TemporaryVariable":
                    produce("   sw t1, -"+str(entity[0].offset)+"(fp)")
                elif entity[0].type == "Parameter":
                    produce("   sw t1, -"+str(entity[0].frameLength)+"(fp)")
            elif quad[1][2] == "REF":
                entity = findVariable(quad[1][1])
                if func_proc_entity[1] == entity[1]:
                    if entity[0].type == "Variable":
                        produce("   addi t0, sp, -"+str(entity[0].offset))
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
                    elif entity[0].type == "Parameter" and entity[0].mode == "in":
                        produce("   addi t0, sp, -"+str(entity[0].offset))
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
                    elif entity[0].type == "Parameter" and entity[0].mode == "inout":
                        produce("   lw t0, -"+str(entity[0].offset)+"(sp)")
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
                else:
                    if entity[0].type == "Variable":
                        gnlvcode(quad[1][1])
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
                    elif entity[0].type == "Parameter" and entity[0].mode == "in":
                        gnlvcode(quad[1][1])
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
                    elif entity[0].type == "Parameter" and entity[0].mode == "inout":
                        gnlvcode(quad[1][1])
                        produce("   lw t0, (t0)")
                        produce("   sw t0, -"+str(entity[0].offset)+"(fp)")
            elif quad[1][2] == "RET":
                entity = findVariable(quad[1][1])
                if entity[0].type == "Variable" or entity[0].type == "TemporaryVariable":
                    produce("   addi t0, sp, -"+str(entity[0].offset))
                    produce("   sw t0, -8(fp)")
                elif entity[0].type == "Parameter":
                    produce("   addi t0, sp, -"+str(entity[0].offset))
                    produce("   sw t0, -8(fp)")
            elif quad[1][0] == "call":
                function_or_procedure_call = 0
                if len(scopes) == func_proc_entity[1]:
                    produce("   lw t0, -4(sp)")
                    produce("   sw t0, -4(fp)")
                else:
                    produce("   sw sp, -4(fp)")
                produce("   addi sp, sp, "+str(func_proc_entity[0].frameLength))
                produce("   jal L"+str(int(func_proc_entity[0].startingQuad)-1))
                produce("   addi sp, sp, -"+str(func_proc_entity[0].frameLength))
        elif quad[1][0] == "halt":
            pass
        elif quad[1][0] == "endblock":
            if quad[1][1] != ID:
                produce("   lw ra, -0(sp)")
                produce("   jr ra")
            else:
                produce("   li a0, 0")
                produce("   li a7, 93")
                produce("   ecall")
    list_of_quads_for_final_code = []
                
################################################################################################################

syntax_analyst()     # run program
intermediate_code()  # creates test.int
c_code()             # creates test.c


Symbol_Table.close() # creates test.symb
FinalCode.close()    # creates test.asm
file.close()         # close test.ci