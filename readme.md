# TinComp - A Compiler for simple programming language

This project is a compiler for a simple high-level programming language resembling the C language. The compiler includes both a frontend and a backend, as well as a type checker. The compilation process produces binary executables runnable on the AMD64 instruction set architecture in a GNU/Linux environment. The compiler works with the Python interpreter (v3.10) without using any libraries outside Python’s standard library or any other dependencies.

The compiler and the programming language largely follow the practices and principles introduced in the course materials of the University of Helsinki’s *Compilers* course \[1].

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

Function call parameters are limited. The compiler does not use the stack to handle "additional" parameters like Linux Calling Convention.

More detailed information about technical solutions of the compiler can be found under the doc directory.

### 1.1 The Compilation Pipeline

The stages of the compilation process are listed below:

1.  Tokenizer (`tokenizer.py`)
    - some desugaring
2.  Parser (`parser.py`)
    *   before actual parsing, the token stream from the tokenizer is processed by desugars
3.  Type checker (`type_checker.py`)
4.  IR generator (`ir_generator.py`)
    - some very basic and common optimizations
5.  Assembly generator (`asm_generator.py`)
    - some very basic and common optimizations

### 1.2 Intermediate Representation (IR)

The intermediate representation is text-based and can therefore be viewed and edited using regular text editors. The IR has a small set of instructions. Each instruction can have up to three parameters.

*   `LoadIntConst(<const[Int]>, <var[]>)`
*   `LoadBoolConst(<const[Bool]>, <var[]>)`
*   `Call(<operation[function|op_code]>, <list_params>, <return_var[]>)`
*   `Jump(<label[]>)`
*   `CondJump(<var|const>, <label[]>)`

Labels are expressed as strings. They begin either with `L` or `.L`.

## 2. Usage

The software needs Python version >= 3.11 and GNU/Linux system e.g. Ubuntu distribution to working. No other dependencies needed. If you want to use the testing tools, install
```
pip install pytest
pip install coverage
```

### 2.1. How to use the compiler?

Programs are compiled into executable binary files by running the script `compile.sh` in the project root directory. If you only want to output text expressed assembly file, add flag -S.

    ./compile <source file name> <object or asm file name> [-S] 

To compile without any optimizations, plase use -O0 flag. (Please note, that you cannot not use both tags on the same time (-S and -O0)!)

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
    return get(get(president, Presidentti->valtio), Valtio->nimi);
}

fun get_presidents_country_population_count(president): Int {
	return get(get(president, Presidentti->valtio), Valtio->asukkaiden_lkm);
}

fun print_president_information(president) {
	var valtio_nimi = get_presidents_country_name(president);
	var valtio_asukkaita = get_presidents_country_population_count(president);
	print_str2(valtio_nimi); print_str2(" asukkaita "); print_int(valtio_asukkaita);
}

// Define the data structure Valtio and Presidentti
define struct Valtio = { nimi, asukkaiden_lkm };
define struct Presidentti = { valtio, nimi, syntymavuosi };

// Create array for the presidents
var presidents = array(2);

var suomi = New(Valtio);
var usa = New(Valtio);

// set the struct fields
set(suomi, Valtio->asukkaiden_lkm, 5500000);
set(suomi, Valtio->nimi, "Suomi");
set(usa, Valtio->asukkaiden_lkm, 331449281);
set(usa, Valtio->nimi, "Amerikan yhdysvallat");

var stubb = New(Presidentti);
var trump = New(Presidentti);

set(stubb, Presidentti->valtio, suomi);
set(stubb, Presidentti->nimi, "Stubb");
set(stubb, Presidentti->syntymavuosi, 1968);

// put the created struct to index 0
set(presidents, 0, stubb);

// set the struct fields
set(trump, Presidentti->valtio, usa);
set(trump, Presidentti->nimi, "Trump");
set(trump, Presidentti->syntymavuosi, 1946);

// put the created struct to index 1
set(presidents, 1, trump);

var i: Int = 0; 
while i < 2 do {	
	var president = get(presidents, i);
	
	print_president_information(president);
	
	if (get(president, Presidentti->syntymavuosi) == 1968) 
			or 
	   (get(president, Presidentti->syntymavuosi) == 1946) then 
	{
		print_str2(str_cat("Presidentin ", get(president, Presidentti->nimi)));
		print_str2(str_cat(" syntymävuosi on ", int_to_str(get(president, Presidentti->syntymavuosi))));
		print_str(" ");
	}
	
	i = i + 1;
}
```
***

## References

\[1] <https://hy-compilers.github.io/spring-2026/>
