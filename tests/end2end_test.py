import sys
import os
sys.path.append('../src/')

from main import main

def read_output():
    output = ""
    with open("output.dat") as f:
        output = f.read()
    os.system("rm output.dat")
    return output

def run_program():
    os.system("./a.out >> output.dat")
    os.system("rm a.out")

def test1():
    main("test_programs/example1.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """5
16
8
4
2
1
"""

def test2():
    try:
        main("test_programs/example3.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert "parsing error after if statement" in str(e)
    
def test3():
    main("test_programs/example4.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """12
"""

def test4():
    main("test_programs/example5.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """10
9
8
7
6
5
4
3
2
10
"""

def test5():
    try:
        main("test_programs/example6.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert "Line 5: parsing error after else statement." in str(e)

def test6():
    try:
        main("test_programs/example7.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert "parsing error after if statement" in str(e)

def test7():
    try:
        main("test_programs/example8.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert "parsing error after while statement" in str(e)

def test8():
    main("test_programs/example9.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """10
9
8
7
6
5
4
3
2
10
9
8
7
6
5
4
3
2
"""

def test9():
    main("test_programs/example10.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """0
1
2
3
4
5
6
7
8
9
0
1
2
3
4
5
6
7
8
9
"""

def test10():
    try:
        main("test_programs/example11.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert True

def test11():
    main("test_programs/example12.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """1
3
"""

def test12():
    main("test_programs/example13.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """15
"""

def test13():
    main("test_programs/example15.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """5
"""

def test19():
    main("test_programs/example22.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """1
0
2
1
0
3
2
1
0
4
3
2
1
0
5
5
"""

def test20():
    try:
        main("test_programs/example23.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert True

def test21():
    try:
        main("test_programs/example24.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert True

def test_case1():
    main("test_programs/test_case1.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """true
9
true
7
true
5
true
3
true
1
true
"""

""" Testing errors. """

def test_case2():
    try:
        main("test_programs/test_case2.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert """Line 3: { must be a literal or an identifier, not BRACE""" in str(e) 

def test_case3():
    try:
        main("test_programs/test_case3.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert """Illegal expression""" in str(e)

def test_case4():
    try:
        main("test_programs/test_case4.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert """parsing error after while statement""" in str(e) 

def test_case5():
    try:
        main("test_programs/test_case5.txt", "a.out", "../src/")
        assert False == True
    except Exception as e:
        assert """Line 4: expecting ; or } but it was )""" in str(e)

def test_case6():
    main("test_programs/test_case6.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """true
true
true
true
true
false
"""

def test_case7():
    main("test_programs/test_case7.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """true
true
true
true
true
true
true
true
true
true
false
"""

def test_case8():
    main("test_programs/test_case8.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """0
1
2
3
4
5
6
7
8
9
true
"""

def test_case9():
    main("test_programs/test_case9.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """0
1
2
3
0
1
2
4
0
1
2
5
0
1
2
false
"""

def test_case10():
    main("test_programs/test_case10.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """0
1
2
3
4
5
6
7
8
true
false
-1
"""

def test_case13():
    main("test_programs/example25.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """hello world
"""


def test_case15():
    try:
        main("test_programs/failing7.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Type error" in str(e)

def test_case16():
    try:
        main("test_programs/failing8.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Type error" in str(e)

def test_case18():
    try:
        main("test_programs/failing10.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Type error" in str(e)

def test_case19():
    try:
        main("test_programs/failing11.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "variable a is out of the context" in str(e)

def test_case20():
    try:
        main("test_programs/failing12.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Type error! Str Int expected Int" in str(e)

def test_case21():
    try:
        main("test_programs/failing13.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Syntax error in line 4 with token {, expected then" in str(e)


def test_case22():
    main("test_programs/example_str1.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hello world!
"""

def test_case23():
    main("test_programs/example_str2.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hello world!
"""

def test_case24():
    main("test_programs/example_str3.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """true
false
"""

def test_case25():
    main("test_programs/example_str4.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hello world!
"""

def test_case26():
    main("test_programs/example_str5.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
"""

def test_case27():
    main("test_programs/example_str6.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """Hello world!
Hello world!
Hello world!
Hello world!
Hello world!
"""

def test_case28():
    try:
        main("test_programs/failing15.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert str(e) == """Line 2: undeclared variable bcd"""

def test_case29():
    try:
        main("test_programs/failing16.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert str(e) == """Line 2: illegal value for Bool type"""

def test_case30():
    main("test_programs/example_str7.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
Hello world!
Hello world!Bye world!
10
2345
Hello world!
2345
"""

def test_case31():
    main("test_programs/example_str8.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """1024
1024
65536
and back to integer type 65536
and back to integer type 65536
"""

def test_case32():
    main("test_programs/complex_program.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """Hello world!!!!!!!!
ello world!!!!!!!!
llo world!!!!!!!!
lo world!!!!!!!!
o world!!!!!!!!
 world!!!!!!!!
world!!!!!!!!
orld!!!!!!!!
rld!!!!!!!!
ld!!!!!!!!
d!!!!!!!!
!!!!!!!!
!!!!!!!
!!!!!!
!!!!!
!!!!
!!!
!!
!
Hello world!
"""

def test_case33():
    main("test_programs/example_str9.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """Hello world!
Hello Joe! 
"""

def test_case34():
    main("test_programs/example_functions1.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hello world
hello world
hello world
hello world
hello world
hello world
"""

def test_case35():
    try:
        main("test_programs/example_functions2.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "variable i is out of the context!" in str(e)

def test_case36():
    try:
        main("test_programs/example_functions3.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "variable j is out of the context!" in str(e)

def test_case37():
    main("test_programs/example_functions4.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hello world on suomeksi hei maailma
"""

def test_case38():
    main("test_programs/example_functions5.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """ saippuakauppias
"""

def test_case39():
    try:
        main("test_programs/example_functions6_fail.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert str(e) == """Unmatch braces in defining function."""

def test_case40():
    try:
        main("test_programs/example_functions7_fail.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert """syntax error in defining function.""" in str(e)

def test_case41():
    try:
        main("test_programs/example_functions8_fail.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert """syntax error in defining function. Expecting ( but it was return""" in str(e) 

def test_case42():
    main("test_programs/example_functions9.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """5
"""

def test_case43():
    main("test_programs/example_functions10.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """ hello hello hello hello 
"""

def test_case44():
    try:
        main("test_programs/example_functions11.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert str(e) == """Line 5: Type error! Int Bool expected same types"""

def test_case45():
    try:
        main("test_programs/example_functions12.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert str(e) == """Line 13: Type error! Bool Int expected same types"""

def test_case46():
    main("test_programs/example_functions13.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """120
"""



def test_case47():
    import subprocess

    main("test_programs/example_userinput.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="5\nq\n",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """Please input a number to get factorial. \\q\\ to exit
>120
>"""

def test_case48():
    main("test_programs/example26.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """saippuakauppias
"""

def test_case49():
    main("test_programs/example_arrays1.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """hei maailma
hello world
hej!
hej!
hej!
hej!
"""

def test_case50():
    main("test_programs/example_arrays2.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """0
2
7
4
51
135
"""

def test_case51():
    main("test_programs/example_arrays3.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """0
1
2
"""

def test_case52():
    main("test_programs/example_arrays4.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """4
3
2
1
0
"""

def test_case53():
    import subprocess

    main("test_programs/example_arrays5.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="moi\nterve\nhei\nmoro\nmorjens\n",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """input string: input string: input string: input string: input string: done!
You typed
moi
terve
hei
moro
morjens
"""

def test_case54():
    try:
        main("test_programs/arrays_failing1.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Illegal array" in str(e)

def test_case55():
    try:
        main("test_programs/arrays_failing2.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Illegal array" in str(e)

def test_case56():
    try:
        main("test_programs/arrays_failing3.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Illegal array" in str(e)

def test_case57():
    try:
        main("test_programs/failing17.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Line 20: Unknown function name: f" in str(e)

def test_case58():
    try:
        main("test_programs/failing18.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Line 21: variable a is not declared before assign" in str(e)

def test_case59():
    try:
        main("test_programs/failing19.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "Line 20: illegal variable name: return" in str(e)

def test_case60():
    try:
        main("test_programs/failing20.txt", "a.out", "../src/")
        assert True
    except Exception as e:
        assert False

def test_case61():
    main("test_programs/comment_test.txt", "a.out", "../src/")
    run_program()

    assert read_output() == "9\n"

def test_case63():
    try:
        main("test_programs/failing22.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "illegal" in str(e)

def test_case64():
    try:
        main("test_programs/failing23.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "cannot define function as name get" in str(e)

def test_case65():
    import subprocess

    main("test_programs/large_program.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="laske\n4\n4\n*\nlaske\n4\n5\n-\n\nlopeta",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """Anna komento: Anna kaksi lukua: Anna operaatio: 
16
Anna komento: Anna kaksi lukua: Anna operaatio: 
-1
Anna komento: Ohjelma lopetetaan.
"""

def test_case66():
    try:
        main("test_programs/variable_redeclaration.txt", "a.out", "../src/")
        assert True
    except Exception as e:
        assert False

def test_case67():
    try:
        main("test_programs/variable_redeclaration2.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "you cannot redeclarate variable input" in str(e)

def test_case68():
    try:
        main("test_programs/variable_redeclaration3.txt", "a.out", "../src/")
        assert True
    except Exception as e:
        assert False

def test_case69():
    try:
        main("test_programs/variable_redeclaration4.txt", "a.out", "../src/")
        assert True
    except Exception as e:
        assert False

def test_case70():
    try:
        main("test_programs/variable_redeclaration5.txt", "a.out", "../src/")
        assert True == False
    except Exception as e:
        assert "you cannot redeclarate variable a" in str(e)

def test_case71():
    main("test_programs/example27.txt", "a.out", "../src/")
    run_program()

    assert read_output() == """-403439616
"""

def test_case72():
    import subprocess

    main("test_programs/large_program2.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="laske\n4\n4\n*\nlaske\n4\n5\n-\n\nlopeta",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """Anna komento: Anna kaksi lukua: Anna operaatio: 
16
Anna komento: Anna kaksi lukua: Anna operaatio: 
-1
Anna komento: Ohjelma lopetetaan.
"""

def test_case73():
    import subprocess

    main("test_programs/large_program3.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="laske\n4\n4\n*\nlaske\n4\n5\n-\n\nlopeta",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """Anna komento: Anna kaksi lukua: Anna operaatio: 
16
Anna komento: Anna kaksi lukua: Anna operaatio: 
-1
Anna komento: Ohjelma lopetetaan.
"""

def test_case74():
    import subprocess

    main("test_programs/large_program4.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="laske\n4\n4\n*\nlaske\n4\n5\n-\n\nlopeta",
        text=True,
        capture_output=True
    )

    assert proc.stdout == """Anna komento: Anna kaksi lukua: Anna operaatio: 
16
Anna komento: Anna kaksi lukua: Anna operaatio: 
-1
Anna komento: Ohjelma lopetetaan.
"""
    
def test_case75():
    try:
        main("test_programs/example_str10.txt", "a.out", "../src/")
        run_program()
        assert read_output() == """Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
"""
    except Exception as e:
        assert False

def test_case76():
    try:
        main("test_programs/complex_program2.txt", "a.out", "../src/")
        run_program()
        assert read_output() == """2128936
"""
    except Exception as e:
        assert False

def test_case77():
    main("test_programs/test_structs.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Suomi
"""

def test_case78():
    main("test_programs/test_structs2.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Suomi
"""

def test_case79():
    main("test_programs/test_structs3.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Suomi asukkaita 5500000
"""

def test_case80():
    main("test_programs/test_structs4.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Suomi asukkaita 5500000
Amerikan yhdysvallat asukkaita 331449281
"""

def test_case81():
    main("test_programs/test_structs5.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Suomi asukkaita 5500000
Presidentin Stubb syntymävuosi on 1968 
Amerikan yhdysvallat asukkaita 331449281
Presidentin Trump syntymävuosi on 1946 
"""

def test_case82():
    main("test_programs/complex_program3.txt", "a.out", "../src/")
    run_program()
    assert read_output() == "242007\n"

def test_case83():
    try:
        main("test_programs/example_externs.txt", "a.out", "../src/")
        assert True == True
    except:
        assert True == False

def test_case84():
    main("test_programs/complex_program4.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """IR Interpreter for Custom language
==================================

Running program with instructions count is 10
Instruction: loadIntConst
  value: 7
  dest_var: x1
Instruction: loadIntConst
  value: 5
  dest_var: tmp5
Call
  operator: >
  params: x1 tmp5
  ret_var: x2
CondJump
  ir_var: x2
  dest: _label_then
Jump
  dest: _label_end
    _label_then
Call
  operator: print_str
  params: \\\\Hello world\\\\
  ret_var: x0
Jump
  dest: _label_end
    _label_end
Call
  operator: print_str
  params: \\\\Bye world\\\\
  ret_var: x0
Program execution completed.
hahaa
"""

def test_case85():
    main("test_programs/example_str11.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Hello world
Im Bob!
Hello world
Im Bob!
Im Alice
Im Alice
Im Bob!
"""

def test_case86():
    main("test_programs/example_str12.txt", "a.out", "../src/")
    run_program()
    assert read_output().replace("\x0e", "") == """I'm [Bob!]
Hello world
I'm [Bob!]Hello world
"""

def test_case89():
    main("test_programs/variable_declaration.txt", "a.out", "../src/")
    run_program()
    assert read_output().replace("\x0e", "") == """I'm [Bob!]
Hello world
I'm [Bob!]I'm [Bob!]
"""

def test_case90():
    main("test_programs/example_str13.txt", "a.out", "../src/")
    run_program()
    assert read_output().replace("\x0e", "") == """I'm [Bob!]

I'm [Bob!]I'm [Bob!]
"""

def test_case91():
    main("test_programs/example_str14.txt", "a.out", "../src/")
    run_program()
    assert read_output().replace("\x0e", "") == """Hello world
I'm [Bob!]

I'm [Bob!]I'm [Bob!]
"""

def test_case92():
    main("test_programs/test_structs6.txt", "a.out", "../src/")
    run_program()
    assert read_output() == """Valtio 0
1917
5600000
Valtio 1
1918
5600001
Valtio 2
1919
5600002
Valtio 3
1920
5600003
Valtio 4
1921
5600004
Valtio 5
1922
5600005
Valtio 6
1923
5600006
Valtio 7
1924
5600007
Valtio 8
1925
5600008
Valtio 9
1926
5600009
"""

def test_case93():
    except_output = """type q to exit
Anna kirjan nimi: 
Anna kirjan painovuosi: 
Anna kirjan hyllypaikka: 
type q to exit
Anna kirjan nimi: 
Anna kirjan painovuosi: 
Anna kirjan hyllypaikka: 
type q to exit
Anna kirjan nimi: 
Kirjan nimi on tuntematon_sotilas painovuosi 1954 ja hyllypaikka 123
Kirjan nimi on taalla_pohjantahden_alla painovuosi 1959 ja hyllypaikka 456
"""

    import subprocess

    main("test_programs/test_structs7.txt", "a.out", "../src/")
    proc = subprocess.run(
        ["./a.out"],
        input="tuntematon_sotilas\n1954\n123\ntaalla_pohjantahden_alla\n1959\n456\nq",
        text=True,
        capture_output=True
    )

    assert proc.stdout == except_output

def test_case94():
    import subprocess

    main("test_programs/hotel_reservation_system.txt", "a.out", "../src/")
    input_data = (
        "reserve\n"
        "10\n"
        "1\n"
        "1\n"
        "3\n"
        "1\n"
        "reserve\n"
        "10\n"
        "5\n"
        "1\n"
        "6\n"
        "1\n"
        "reserve\n"
        "25\n"
        "10\n"
        "2\n"
        "12\n"
        "2\n"
        "reserve\n"
        "10\n"
        "2\n"
        "1\n"
        "4\n"
        "1\n"
        "print_all\n"
        "exit\n"
    )

    proc = subprocess.run(
        ["./a.out"],
        input=input_data,
        text=True,
        capture_output=True
    )

    assert proc.stdout.count("Varaus onnistui.") == 3
    assert "Varaus epaonnistui: paallekkainen varaus." in proc.stdout
    assert "Huone 10 : 1.1 - 3.1" in proc.stdout
    assert "Huone 10 : 5.1 - 6.1" in proc.stdout
    assert "Huone 25 : 10.2 - 12.2" in proc.stdout

def test_case95():
    import subprocess

    main("test_programs/hotel_reservation_system2.txt", "a.out", "../src/")
    input_data = (
        "reserve\n"
        "10\n"
        "1\n"
        "1\n"
        "3\n"
        "1\n"
        "reserve\n"
        "10\n"
        "5\n"
        "1\n"
        "6\n"
        "1\n"
        "reserve\n"
        "25\n"
        "10\n"
        "2\n"
        "12\n"
        "2\n"
        "reserve\n"
        "10\n"
        "2\n"
        "1\n"
        "4\n"
        "1\n"
        "print_all\n"
        "exit\n"
    )

    proc = subprocess.run(
        ["./a.out"],
        input=input_data,
        text=True,
        capture_output=True
    )

    assert proc.stdout.count("Varaus onnistui.") == 3
    assert "Varaus epaonnistui: paallekkainen varaus." in proc.stdout
    assert "Huone 10 : 1.1 - 3.1" in proc.stdout
    assert "Huone 10 : 5.1 - 6.1" in proc.stdout
    assert "Huone 25 : 10.2 - 12.2" in proc.stdout