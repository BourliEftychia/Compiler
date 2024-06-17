Implementation of the translator for the C-imple language

**Purpose of the Exercise:**
Through this assignment, I aim to understand the basic concepts of compiler theory and implement a compiler for the programming language Cimple. This will enable me to later develop compilers for any other language.

**Summary:**
The report begins with an analysis of the parts of the code implemented in Python, followed by examples I executed along with the results printed by my program.
The code consists of five parts: the lexical analyzer, the syntactic analyzer, the intermediate code, the semantic analyzer (symbol table), and the final code.

**Lexical Analyzer:**
The purpose of the lexical analyzer is to recognize all the symbols of the language I am compiling. Its job is to read the file with the language code, break it into packets/lexical units, and identify if the packet represents a variable, number, reserved word, or symbol, and return this packet along with an identifier that indicates the packet's nature. If the packet does not belong to any category, an error message is returned.
Below follows the automaton according to which I categorize the lexical units of the Cimple language, along with some information about its implementation.

**Automaton**

In the lexical analyzer, I assign values to the global variables:
- Word_unit, which holds the lexical unit
- Identifier, which is the identifier of the lexical unit

Additionally, for each line change, I update the variable Line, so I know which line of the program the lexical unit is on.

If I do not use the next character for the lexical unit, I move the pointer one position back to read it again for the next unit.

In case of an error, I move to state -1.

**Syntactic Analyzer:**
I constructed a recursive descent parser based on LL(1) grammar, which checks for syntax errors.
It calls the lexical analyzer to assign values to the global variables and, after consuming the lexical unit, calls it again to get the next one.
In case of an error, it prints the corresponding error message and indicates the line in the Cimple code where the error occurred, as well as which method of my program caused the error, making it easy to locate any errors.
If the code is correct, my program terminates without printing anything.

**Theory:**
**LL(1) Grammar:**

1. Given a specific non-terminal symbol, the first rule of the grammar is applied.
2. In the propositional form that results, the first non-terminal symbol from the left is selected, and the first rule referring to it is applied.
3. Step 2 is applied iteratively for each non-terminal symbol that follows until:
   - a sequence of terminal symbols (language sentence) is produced, or
   - a portion of terminal symbols of the propositional form differs from the corresponding portion of the input string

**Intermediate Code:**
**Theory:**

I implemented the helper subroutines (genquad(): to create a new quadruple, newtemp(): to create a new temporary variable, emptylist(): to create an empty list, makelist(x): to create a list containing only the given argument, merge(list1,list2): to merge two lists, backpatch(): to complete the last field of the quadruple) and used them within the structures I had already constructed for the syntactic analyzer. For my convenience, and yours, for each new line I added or changed in the original syntactic analyzer code for the intermediate code implementation, I added the comment "# intermediate code" next to it.
I print the quadruples text I generate into a text file named "test.int".

Next, in c_code(), I translated the program into C and ran it to verify that the structures I built are functioning correctly so far (test.c).

**Symbol Table:**
The symbol table is part of the semantic analysis. It holds information about all entities (variables, functions, and procedures) in the code, regarding the depth they are located at. Through the symbol table, I can extract information about each entity's scope (e.g., whether a variable is local, global, or an argument that belongs elsewhere).
To implement the symbol table, I created classes/objects and defined fields for them.
- class Scope: Defines a new level. Fields include the depth (level), the entries it contains (entities), and the offset.
- class Entity: Defines an entry.
  The following objects constitute the different types of entries:
  - class Variable: Defines a variable entry (type), including its name, data type, and offset.
  - class FormalParameter: Defines a formal parameter entry (type), including its name, data type, and mode.
  - class Procedure: Defines a procedure entry (type), including its name, starting quad, frame length, and formal parameters.
  - class TemporaryVariable: Defines a temporary variable entry (type), including its name, data type, and offset.
  - class Parameter: Defines a parameter entry (type), including its name, data type, offset, and mode.
  - class Function: Defines a function entry (type), including its name, starting quad, frame length, and formal parameters.

I implemented helper functions (addScope(): to add a new level, deleteScope(): to delete a level, addEntity(): to add an entity entry, startingQuad(): to fill the starting quad field of a function or procedure, frameLength(): to fill the field of a function or procedure that holds the memory needed for return, addFormalParameter(): to add parameters to a function or procedure, searchEntity(): to search for an entry in the symbol table) and a global stack "scopes", where I keep the levels, each containing a table with the entities it includes. In symbolTable(), I generate the file "test.symb" where I dynamically store the symbol table. This method is called at the end of the creation of each block; I read the content of the scopes stack at that moment and update the symbol table file with its data. Next to each new line I added, I included the comment "# symbol table".

Finally, with the searchEntity() method, I perform semantic analysis, essentially checking if the given variable has been declared somewhere earlier (# semantic analyst).

**Final Code:**
In the final code phase, the process of translating the Cimple code into assembly language occurs, using the structures I implemented for the intermediate code and the symbol table.
For the final code, I implemented the requested helper functions (gnlvcode(v): gives access to a variable or address not locally owned, loadvr(v, reg): finds a variable from memory and stores it in a register, storerv(reg, v): reads the variable from a register and stores it in memory, produce(): creates a new line in the final code) + the findVariable() which searches for an entry by its name in the symbol table (scopes) and returns an array where the first position contains this entry and the second the level it is located at.
Finally, in final_code(), I dynamically update the final code by writing it to the file "test.asm". This method is called at the end of each block.

Below I provide some examples I have tested along with the solutions printed by my program. (test.c is created only for programs that do not contain functions or procedures. This check is done with a global variable that acts as a flag and is activated within subprograms()).
At the end, I also provide the codes in case you want to run them yourself.
(In the second phase, I also submitted a txt file containing codes I ran and tested to verify my code).

Test 1

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/d5896be3-b3a1-41c9-9645-31dc46afde1f)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/8fe735a2-e2d8-4a1d-a831-d62e0acaf54b)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/ed04900c-98bc-40cb-8f4c-921dbd04c0f9)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/f7fbebad-3115-4a2c-9ff7-e998c0604938)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/f7709a75-7295-4e61-bb98-4620341b8456)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/572e02da-7b92-4f65-b333-1385bc6d0f52)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/7b4506cd-5c00-4ea0-9f64-6bb81ced288b)

Here we see that the factorial program runs and calculates x correctly! of the number x that we give as input.

Test 2

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/11122577-72bb-4ac5-a58e-8e8cbab46dfb)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/bb976429-e4df-45f4-bd9b-28801cd881e9)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/d2b06a73-9b32-4d2a-b173-70101c836abb)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/cbf0ce44-9ff0-4d43-9db6-eee6ef843326)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/4d3bf21c-8fdc-42a3-add5-4295a9e38036)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/a75980d1-1d2b-49a9-82c9-3815ccbc975f)

Test 3

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/d9550462-c785-45d9-b894-69df06f24b3a)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/55f218da-453b-4e78-8969-d3d79b8bdbb5)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/4dd86325-ab4c-4393-89f0-e922f096acd1)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/0a861777-082a-4900-968a-e19ff366ddc3)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/d304186a-b12d-44ba-a9f6-cb5d880e748e)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/51a050f0-b3da-4a38-8c77-3062e7ce7d44)

Test 4

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/43255d15-3593-4e68-8dd3-989300baf24c)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/1725925c-54e6-4eaf-8745-fd81fc6e4a28)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/86d047c0-0593-451f-b959-e14ea099f0b2)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/308b4ed1-d6f6-488d-b372-a365216c03d7)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/82cca256-3672-41b5-8417-919fe4841f00)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/2a915325-f017-4f4c-9e41-ff4fe5201cf2)

![image](https://github.com/BourliEftychia/Compiler/assets/72252284/99a83307-1dbd-4327-852c-2cc46efc9356)

Here we see that the count digit program runs and correctly calculates the number of numbers we give as input.

