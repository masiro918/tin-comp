# TinComp - A Compiler for simple programming language

This project is a compiler for a simple imperative and recursive programming language resembling the C language. The compiler includes both a frontend (e.g. parser, simple type checking) and a backend (assembly code generation). The compilation process produces binary executables runnable on the AMD64 instruction set architecture in a GNU/Linux environment using AMD64 System V Calling Convention. The compiler works with the CPython interpreter (v3.10) without using any libraries outside Python’s standard library or any other dependencies in the software distribution.

Despite of some different implement strategies and choices, the compiler and the programming language largely follow the practices and principles introduced in the course materials of the University of Helsinki’s *Compilers* course \[1].

## 0. Introduction

Below is a brief overview of the current features. If you want to jump directly to instructions on how to use the compiler, please skip to section 2.

### 0.1 Features

*   `while` loop with `break` and `continue`
*   a simple if-else structure with common comparison properties
*   a few built-in functions
*   data types: integer and boolean
*   simple strings features
*   common binary operations (`+`, `-`, `*`, `/`, `%`)
*   contexts
*   custom functions
*   simple structure system

### 0.2 Limitations

*   the number of local variables is limited
*   the internal code quality is ***very poor*** and should be improved

### 0.3 Future Plans

In the future, I aim to (if I even try) add the following to the programming language:

*   `break` and `continue` in loops ✔️
*   strings (using the standard library, string pool) ✔️
*   user-defined functions ✔️
*   arrays ✔️
*   new data type: 8‑bit unsigned int (`char`) ☐
    - these features are integrated with strings
*   a more extensive standard library ☐
*   structs  ✔️

And more "cosmetic" todos:

*   better error messages ☐
*   overall better user experience and in illegal input for the compiler cannot cause crash ☐

## 1. Technical Overview

The compilation process is staged. After each stage, a new processed result is produced from the previous stage’s output. At a high level, the compilation process can be viewed as two-phase. The first phase converts the source code into an *intermediate representation* (IR), which in the second phase is translated into AMD64 assembly using AT\&T syntax. The resulting assembly code is assembled into an object file using the system’s default assembler.

Function call parameters are limited. The compiler does not use the stack to handle "additional" parameters like System V AMD64 Calling Convention.

More detailed information about technical solutions of the compiler can be found under the doc directory.

### 1.1 The Compilation Pipeline

The stages of the compilation process are listed below:

**Preprocessing**

0.	Detects the functions and struct definitions in the code and parses these expression.

**Frontend**
1.  Tokenizer
    - some desugaring
2.  Parser
    *   before actual parsing, the token stream from the tokenizer is processed by desugars
3.  Type checker
4.  IR generator
    - some very basic and common optimizations 

**Backend**

5. Assembly generator (`asm_generator.py`)
   - some very basic and common optimizations

### 1.2 Intermediate Representation (IR)

The intermediate representation has a small set of instructions. Each instruction can have up to three parameters.

*   `LoadIntConst(<const[Int]>, <var[]>)`
*   `LoadBoolConst(<const[Bool]>, <var[]>)`
*   `Call(<operation[function|op_code]>, <list_params>, <return_var[]>)`
*   `Jump(<label[]>)`
*   `CondJump(<var|const>, <label[]>)`
*	`Ret()`

Labels are expressed as strings. They begin either with `L` or `.L`.

## 2. Usage

The software needs Python version >= 3.11 and GNU/Linux system e.g. Ubuntu distribution to working. No other dependencies needed. If you want to use the testing tools and other dependencies needed to build the software, install by using **pip**
```
pip install -r dev-requirements.txt
```

To build the software:

```
./make_prod_build.sh
```

This script creates executable and other files needed in the production environment into directory **src/dist/main**

### 2.1. How to use the compiler?

Programs are compiled into executable binary files by running the script `compile.sh` in the project root directory. If you only want to output text expressed assembly file, add flag -S.

    ./compile <source file name> <object or asm file name> [-S] 

If you use the production version

    ./tincomp <source file name> <object or asm file name> [-S] 

A quick guide to the programming language can be found in the `doc` directory.

### 2.2 Examples

**Example 1 illustrating language features:**

    var b = true;
    var i = 10;
    
    while i >= 0 do {
        var a = i;
    
        if a % 2 == 0 then {
            var j: Int = 0;
    
            while j < 3 do {
                print_bool(b);
                j = j + 1;
            }
            a = a - 1;
        } else {
            print_int(a);
            a = a - 1;
        }
        i = a;
    }

**Example 2 illustrating language features: (user input, string to int and recursion):**
```
fun factorial(decimal): Int {
	if decimal > 1 then {
		return factorial(decimal - 1) * decimal;
	}
	
	return 1;
}
```

**Example 3 illustrating language features: (arrays):**
```
// bubble sort
fun sort(numbers, count) {
	var i: Int = 0;
    while i < count do {
		var j: Int = 0;
		while j < (count - i - 1) do {
            if get(numbers, j) > get(numbers, j+1) then {
                var temp = get(numbers, j);
                set(numbers, j, get(numbers, j+1));
                set(numbers, j+1, temp);
            }
            j = j + 1;
        }
        i = i + 1;
    }
}

/*
 * main program
 */
fun begin() {
    var numbers = array(100);
    var input = create_empty_str();

    print_str("Input integers (type stop to exit):");

    var n: Int = 0;
    while n < 100 do {
        print_str2("> ");
        input = input_str();

        if str_cmp(input, "stop") then { break; }

        var number = str_to_int(input);        
        set(numbers, n, number);

        n = n + 1;
    }

	sort(numbers, n);

    // Print sorted numbers
    print_str("Sorted numbers:");
    var i = 0;
    while i < n do {
		print_int(get(numbers, i));
		i = i + 1;
	}
}

// call the main program
begin();
```

**Example 4 illustrating language features: (strucs, string, arrays):**
```
fun get_presidents_country_name(president): Str {
    return read_long(read_long(president, Presidentti->valtio), Valtio->nimi);
}

fun get_presidents_country_population_count(president): Int {
	return read_long(read_long(president, Presidentti->valtio), Valtio->asukkaiden_lkm);
}

fun print_president_information(president) {
	var valtio_nimi = get_presidents_country_name(president);
	var valtio_asukkaita = get_presidents_country_population_count(president);
	print_str2(valtio_nimi); print_str2(" asukkaita "); print_int(valtio_asukkaita);
}


define struct Valtio = { nimi, asukkaiden_lkm };
define struct Presidentti = { valtio, nimi, syntymavuosi };

var presidents = array(2);

var suomi = New(Valtio);
var usa = New(Valtio);

write_long(suomi, Valtio->asukkaiden_lkm, 5500000);
write_long(suomi, Valtio->nimi, "Suomi");
write_long(usa, Valtio->asukkaiden_lkm, 331449281);
write_long(usa, Valtio->nimi, "Amerikan yhdysvallat");

var stubb = New(Presidentti);
var trump = New(Presidentti);

write_long(stubb, Presidentti->valtio, suomi);
write_long(stubb, Presidentti->nimi, "Stubb");
write_long(stubb, Presidentti->syntymavuosi, 1968);

set(presidents, 0, stubb);

write_long(trump, Presidentti->valtio, usa);
write_long(trump, Presidentti->nimi, "Trump");
write_long(trump, Presidentti->syntymavuosi, 1946);

set(presidents, 1, trump);

var i = 0; while i < 2 do {	
	var president = get(presidents, i);
	print_president_information(president);
	
	if (read_long(president, Presidentti->syntymavuosi) == 1968) or (read_long(president, Presidentti->syntymavuosi) == 1946)
	then {
		print_str2(str_cat("Presidentin ", read_long(president, Presidentti->nimi)));
		print_str2(str_cat(" syntymävuosi on ", int_to_str(read_long(president, Presidentti->syntymavuosi))));
		print_str(" ");
	}
i = i + 1;}
```
***

## References

\[1] <https://hy-compilers.github.io/spring-2026/>
