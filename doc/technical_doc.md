**Attention! This documentation is still very much in progress.**
-----------------------------------------
# Technical Solutions and Overview

Programming language structures are hierarchical. The diagram below shows that a structure can contain structures with an arrow pointing away from them. For example, a VariableAssign can contain an Expression, which covers mathematical expressions, constants, variables, and function calls. However, a VariableAssign cannot contain an if-statement or a context start or end (=block). On the other hand, an if-statement can (and must) contain a binary operation and an expression. An Expression is the most complex of the structures. Its structures can be recursive, meaning they can repeat themselves. For example 

``` f(f(f(x + f(x))))) - 2 / g(f(g(x)))) ```

## Data Structures

TODO: kaaviokuva ast-hierarkiasta

## Tokenizing and Parsing

- aluksi poimitaan funktiot ja käsitellään ne sellaisian
  - lisätään tokeneihin tiedot rivinumeroista
  - se koodi, mikä ei ole minkään funktion sisällä, tulkitaan main-funktioksi

- desugars etc.
  - TODO: lisätään { } -> eli tulee yksi top-level konteksti
  - listään kontekstin loppuun ; koska parseri vaatii, mutta kielen käyttäjälle se ei näyttäydy niin
  - uudelleennimetään muuttujat, jotta sanat eivät mene sekaisin funktioiden kanssa

- The parser is recursive descent parser. On the high-level description, the parser runs through the tokens and looks one or two tokens that the index pointer indicates. The parser interprets the coming expression in the token list by the tokens and creates the abstract syntax tree.

## Types and Type Checking

- about strings and why string are ints but cannot be changes (immutable)
- compiler checks types of comparing operands, nothing else
  - **only compare operations are type checked!** Not function parameters and variable declarations, if variable's type is not defined
  - for example: var a: Bool = 7; is ok and pow2(input_str()); , but var y = 7 + input_str(); is not


## IR Generation

- Checks that variable declarations and assignments are correct
  - this is used by stack data structure -> when a new context is defined, we create a new "context" into the stack and also previous context are available, but if the current context is ending, we pop the latex context from the stack and the variables declared inside the latest context is not available anymore

## Assembly Generation

- What are the instructions that the compilers uses?
- No optimizing
- Assembly generator and IR: is asm generator expecting specific variables of the IR?
  - maybe in the future it would be better to strongly separate frontend and backend
  - variable rename: adding prefix: why? IR does not require specific variable names but the assembly generator needs
  - variables are mapped into rbp-register based by 1:1 -> e.g. x1 => -8(%rbp) and x2 => -16(%rbp)
  - currently the stack size is a constant: 1024 bytes, so the maximum count of the variables is 128
  - boolean values is in fact integers 1 and 2
  - strings and other data typed variables is expressed as a pointer that indicated into memory locations
- function call routines follow System V 64-bit Calling Convention, but the number of function parameters is limited because we don't use the stack for additional parameters
  - user-defined functions are fully "subprograms": the language (and compiler) does not support global variables so there is only a one way to share information between functions: function parameters
  - the compiler handles functions separately on by one throw the compilation pipeline and returns compiled assembly code, statements there don't below any functions are interpreted as "main" function where the execution starts. Finally the compiler constructs the program by compiled functions



## Testing

* CI pipeline
* coverage
