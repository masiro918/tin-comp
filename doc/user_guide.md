# Quick Guide to the Programming Language

This short manual guides you programming with the programming language. After reading this document you are (hopefully) familiar with the language structure and restrictions of the language.

### Contents

1.  Main Structures
2.  Strings
3.  Arrays
4.  VERY Important to know

---

## 1. Main Structures

The language is recursive. For example:

    if a > f(x * g(x + 1)) then { .... }

On the right side of the comparison expression, there are nested function calls and mathematical expressions.  
However, something like `if if (a == true)` is not valid. So you cannot express any strucutures as recursively.

Like in the C programming language, variable **contexts** (or scopes) are used. A lower-level context may reference variables that exist in earlier and at least equally high-level contexts.

### More detailed definition of the language

*   variable declaration  
    `var <variable_name> = [expr];`  
    `var <variable_name>: [type] = [expr];`

*   conditional statement  
    `if [BinOp] then { [statement1]; ...; [statementN] } else { [statement1]; ...; [statementN] }`  
    `if [BinOp] then { [statement1]; ...; [statementN] }`

*   while loop  
    `while [BinOp] do { [statement1]; ...; [statementN] }`
      - you can command the "force exit" from the loop by `break` 
      - you can command the execution to the beginning of the loop by `continue`

*   updating the value of an already defined variable  
    `<variable_name> = [expr];`
    
*   negative numbers consists **a significant detail**: if you type -1, this is interpret as negative number BUT with whitespace - 1, it is illegal expression: the it is an math operation. So if you want to express calculation a - 10, type with whitespace
    
* you can define your own functions using

      fun <function name> ([var1, ..., varN]): [return type] { 
          [statement1]; ...; [statementN];
          [return value];
      }

​	Defining return type is optional. If return type is not defined, it is assumed as **Int**. Also return value is 
​	optional. **The maximum number of the parameters is 6. The compiler does not use the stack for possible additional parameters.**

**Expr** is a mathematical expression, which may also contain function calls that return some value. A boolean value is also valid, but the types of the expression must be compatible with each others.

**BinOp** is of the form `[expr] op [expr]`, where both expressions must return the same type.

The following operators are allowed:

    > < >= <= == != or

**NOTE!** The last statement inside a context does not necessarily require a semicolon; it is optional.

***

## 2. Strings

Strings are implemented using the so-called **string pool** technique. An array (or memory area) is created in the generated ELF file, and strings are stored there. The size of the array is 64k bytes, so this is the current limit for strings. Strings are manipulated using functions provided by the included standard library.

Strings are created the same way as any other variable:

    var s1 = "Hello world!";

Here we can note an interesting detail: the above variable initialization actually creates an *Int*-typed variable `s1` and assigns it the return value of the function `Str` with the parameter `"Hello world!"`. This function call is performed automatically by the compiler, and the programming language user does not need to care about it — but it's useful to understand it. The `Str` function stores the string `"Hello world!"` in the string pool area and returns the memory address where the string begins.

However, it's important for the programmer to know that `s1` is an integer referring to a memory location. If you are familiar with C language, this may not be a problem to understand the mechanics.

Strings can be manipulated with the following functions:

*   **str\_cmp(s1: IntRef, s2: IntRef): Bool**
    *   compares two string references. Returns *true* if they are equal, otherwise *false*.
*   **str\_cat(s1: IntRef, s2: IntRef): Int**
    *   concatenates the two strings and returns a **reference** to the newly created combined string.
*   **str\_len(s1: IntRef): Int**
    *   returns the length of the string.
*   **print\_str(s: Int)**
    *   prints the string referenced by *s* (NOTE! Prints a linebreak at the end.)
*   **print\_str2(s: Int)**
    *   prints the string referenced by *s* (NOTE! Does *not* print a linebreak.)
*   **str\_to\_int(s: Int): Int**
    *   converts a string to an integer.
*   **int\_to\_str(s: Int): Int**
    *   converts an integer to a string.
*   **get\_char\_from\_str(s: Int, index: Int): IntRef**
    *   extracts a character from the string `s` at position `index` and returns a reference to the extracted character (creates a new single-character string!).
*   **input\_str(): Int**
    *   gets user input (stdin) and returns reference to the inputed string
*   **create_empty_str(): Int**
    *   creates empty string and returns reference to the created string

_**IntRef** is a real integer but it is also memory address for the string. Be careful if you manipulate the value, it is possible to reference out of the string!_

## 3. Arrays

A one-dimensional array is created as follows:

    	var arr = array(SIZE);

where `SIZE` is a positive integer constant. It CANNOT be a variable or any kind of *expression*, because the memory required by the array is allocated already at compile time. Like strings, `arr` is a reference to a memory address where the first element of the array resides. Therefore, if you write for example `new_arr = arr;` and then modify element X of the array `arr`, you will also be modifying element X of the array `new_arr`. This happens precisely because both variables refer to the same first element of the array. So remember that a variable is not the array itself but a *reference*! It may also be important and interesting to realize that `array(N)` is not a function call, even though syntactically it looks like one.

Only integers are actually stored in an array. However, you can seemingly store strings and boolean values in an array as well. Why? Strings appear as strings, but they are also references to memory locations, i.e. they are integers. Boolean values, in turn, are in reality the integers 1 and 0, so they are acceptable for the same reason. In this language, type checking is performed only for binary operators and variable declarations, not for function parameters.

You can insert a value into an array with

    	set(arr, L, X);

where `L` is the position in the array, `arr` is the array, and `X` is the value. `L` and `X` are *expressions*.

You can retrieve an element from an array with

    	var val = get(arr, L);

where `L` is the position in the array. This function returns an integer.

## 4. VERY Important to know


There are several important and significant restrictions and bugs to important to know when using the compiler.

- a string cannot be returned as a constant from a function
  - i.e. the following is not allowed: ```return "hello world";```
  - if a string is returned, return it as a variable or as a call to another function
    - e.g. ```return str_cat(create_empty_str(), "hello world");```
- be careful if you set the return value of a function to Str OR define a variable as Str
  - it is best not to define a type for strings at all
  - when defining the type Str, you may encounter unexpected and strange type checking errors
- you can name variables with function names, but even then the end result is completely uncertain
- in some situations the error messages can be very vague

## 4.1. Recommendations and good practices

- although it is possible to write the main program without any function, do it in a function called begin, which is called
  - this way you avoid certain rare bugs related to error messages reported by the compiler
  
- use type declarations for variables and function return values ​​only if they are of type bool or int
  - otherwise do not declare a type for variables or functions
  
- if you initialize a string without an initial value, use create_empty_str() fuction to set the variable's inital value, for example ```var a = create_empty_str();```

  
