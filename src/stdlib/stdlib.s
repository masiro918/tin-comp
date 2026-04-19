/**
Copyright (C) 2026 Matias Siro

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
        
.LL9:
	.text
	.globl	pow2
	.type	pow2, @function
pow2:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq    $32, %rsp    # reserve 32 bytes for locals

	# implementation startrs
	xorq	%rax, %rax
	movq	%rdi, %rax
	imulq	%rax, %rax
	
	# implementation ends
	movq   %rbp, %rsp
    popq   %rbp
	ret

.LL10:
	.text
	.globl power
	.type power, @function
power:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp	# reserve 32 bytes for locals

	# call	pow@PLT

	# implementation ends
	movq   %rbp, %rsp
    popq   %rbp
	ret

.input:
	.string	"%d\n"
	.text
	.globl print_int
	.type print_int, @function

print_int:
	
	pushq  %rbp
    movq   %rsp, %rbp
    subq   $32, %rsp    # reserve 32 bytes for locals

	# implementation startrs
	movl %edi, -4(%rbp)
	movl -4(%rbp), %eax
	movl %eax, %esi
	leaq .input(%rip), %rax
	movq %rax, %rdi
	movl $0, %eax
	call printf@PLT

	# implementation ends
	movq   %rbp, %rsp
    popq   %rbp
	ret
	


.LC0:
	.string	"true"
.LC1:
	.string	"false"
	.text
	.globl	print_bool
	.type	print_bool, @function
print_bool:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp	# reserve 32 bytes for locals

	# implementation starts
	movl	%edi, -4(%rbp)
	cmpl	$1, -4(%rbp)
	jne	.LABEL2
	leaq	.LC0(%rip), %rax
	movq	%rax, %rdi
	call	puts@PLT
	jmp .END
.LABEL2:
	leaq	.LC1(%rip), %rax
	movq	%rax, %rdi
	call	puts@PLT
	
.END:
	# implementation ends
	movq   %rbp, %rsp
    popq   %rbp
	ret

	.text
	.globl	ptr
	.bss
	.align 4
	.type	ptr, @object
	.size	ptr, 4
ptr:
	.zero	4
	.globl	__mem
	.align 32
	.type	__mem, @object
	.size	__mem, 4294967296
__mem:
	.zero	4294967296
	.text
	.globl	str_len
	.type	str_len, @function
str_len:
.L_FB0:
	
	pushq	%rbp
	movq	%rsp, %rbp
	movl	%edi, -20(%rbp)
	movl	-20(%rbp), %eax
	movl	%eax, -8(%rbp)
	movl	$0, -4(%rbp)
	jmp	.L_2
.L_3:
	addl	$1, -8(%rbp)
	addl	$1, -4(%rbp)
.L_2:
	movl	-8(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	testb	%al, %al
	jne	.L_3
	movl	-4(%rbp), %eax
	popq	%rbp
	ret
.L_FE0:
	.size	str_len, .-str_len
	.globl	str_cmp
	.type	str_cmp, @function
str_cmp:
.L_FB1:
	
	pushq	%rbp
	movq	%rsp, %rbp
	pushq	%rbx
	subq	$24, %rsp
	movl	%edi, -28(%rbp)
	movl	%esi, -32(%rbp)
	movl	-28(%rbp), %eax
	movl	%eax, %edi
	call	str_len
	movl	%eax, %ebx
	movl	-32(%rbp), %eax
	movl	%eax, %edi
	call	str_len
	cmpl	%eax, %ebx
	je	.L_6
	movl	$0, %eax
	jmp	.L_7
.L_6:
	movl	$0, -16(%rbp)
	movl	-32(%rbp), %eax
	movl	%eax, %edi
	call	str_len
	movl	%eax, -12(%rbp)
	jmp	.L_8
.L_10:
	movl	-28(%rbp), %edx
	movl	-16(%rbp), %eax
	addl	%edx, %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %edx
	movl	-32(%rbp), %ecx
	movl	-16(%rbp), %eax
	addl	%ecx, %eax
	cltq
	leaq	__mem(%rip), %rcx
	movzbl	(%rax,%rcx), %eax
	cmpb	%al, %dl
	je	.L_9
	movl	$0, %eax
	jmp	.L_7
.L_9:
	addl	$1, -16(%rbp)
.L_8:
	movl	-16(%rbp), %eax
	cmpl	-12(%rbp), %eax
	jl	.L_10
	movl	$1, %eax
.L_7:
	movq	-8(%rbp), %rbx
	leave
	ret
.L_FE1:
	.size	str_cmp, .-str_cmp
	.globl	str_cat
	.type	str_cat, @function
str_cat:
.L_FB2:
	
	pushq	%rbp
	movq	%rsp, %rbp
	movl	%edi, -20(%rbp)
	movl	%esi, -24(%rbp)
	movl	ptr(%rip), %eax
	movl	%eax, -4(%rbp)
	movl	-20(%rbp), %eax
	movl	%eax, -8(%rbp)
	jmp	.L_12
.L_13:
	movl	ptr(%rip), %ecx
	movl	-8(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %edx
	movslq	%ecx, %rax
	leaq	__mem(%rip), %rcx
	movb	%dl, (%rax,%rcx)
	movl	ptr(%rip), %eax
	addl	$1, %eax
	movl	%eax, ptr(%rip)
	addl	$1, -8(%rbp)
.L_12:
	movl	-8(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	testb	%al, %al
	jne	.L_13
	movl	-24(%rbp), %eax
	movl	%eax, -8(%rbp)
	jmp	.L_14
.L_15:
	movl	ptr(%rip), %ecx
	movl	-8(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %edx
	movslq	%ecx, %rax
	leaq	__mem(%rip), %rcx
	movb	%dl, (%rax,%rcx)
	movl	ptr(%rip), %eax
	addl	$1, %eax
	movl	%eax, ptr(%rip)
	addl	$1, -8(%rbp)
.L_14:
	movl	-8(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	testb	%al, %al
	jne	.L_15
	movl	ptr(%rip), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movb	$0, (%rax,%rdx)
	movl	ptr(%rip), %eax
	addl	$1, %eax
	movl	%eax, ptr(%rip)
	movl	-4(%rbp), %eax
	popq	%rbp
	ret
.L_FE2:
	.size	str_cat, .-str_cat
	.globl	print_str
	.type	print_str, @function
print_str:
.L_FB3:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp
	movl	%edi, -20(%rbp)
	movl	-20(%rbp), %eax
	movl	%eax, -4(%rbp)
	jmp	.L_18
.L_19:
	movl	-4(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	movzbl	%al, %eax
	movl	%eax, %edi
	call	putchar@PLT
	addl	$1, -4(%rbp)
.L_18:
	movl	-4(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	testb	%al, %al
	jne	.L_19
	movl	$10, %edi
	call	putchar@PLT
	leave
	ret
.L_FE3:
	.size	print_str, .-print_str
	.globl	print_str2
	.type	print_str2, @function
print_str2:
.L2_FB3:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp
	movl	%edi, -20(%rbp)
	movl	-20(%rbp), %eax
	movl	%eax, -4(%rbp)
	jmp	.L2_18
.L2_19:
	movl	-4(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	movzbl	%al, %eax
	movl	%eax, %edi
	call	putchar@PLT
	addl	$1, -4(%rbp)
.L2_18:
	movl	-4(%rbp), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movzbl	(%rax,%rdx), %eax
	testb	%al, %al
	jne	.L2_19
	leave
	ret
.L2_FE3:
	.size	print_str2, .-print_str2
	.globl	Str
	.type	Str, @function
Str:
.L_FB4:
	
	pushq	%rbp
	movq	%rsp, %rbp
	movq	%rdi, -24(%rbp)
	movl	ptr(%rip), %eax
	movl	%eax, -4(%rbp)
	movl	$0, -8(%rbp)
	jmp	.L_21
.L_22:
	movl	-8(%rbp), %eax
	movslq	%eax, %rdx
	movq	-24(%rbp), %rax
	addq	%rax, %rdx
	movl	ptr(%rip), %eax
	movzbl	(%rdx), %edx
	cltq
	leaq	__mem(%rip), %rcx
	movb	%dl, (%rax,%rcx)
	movl	ptr(%rip), %eax
	addl	$1, %eax
	movl	%eax, ptr(%rip)
	addl	$1, -8(%rbp)
.L_21:
	movl	-8(%rbp), %eax
	movslq	%eax, %rdx
	movq	-24(%rbp), %rax
	addq	%rdx, %rax
	movzbl	(%rax), %eax
	testb	%al, %al
	jne	.L_22
	movl	ptr(%rip), %eax
	cltq
	leaq	__mem(%rip), %rdx
	movb	$0, (%rax,%rdx)
	movl	ptr(%rip), %eax
	addl	$1, %eax
	movl	%eax, ptr(%rip)
	movl	-4(%rbp), %eax
	popq	%rbp
	ret
.L_FE4:
	.size	Str, .-Str
	.section	.rodata
.L_C0:
	.string	"%d\n"
	
        .text
        .globl  str_to_int
        .type   str_to_int, @function
str_to_int:
        
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $112, %rsp
        movl    %edi, -100(%rbp)
        movq    %fs:40, %rax
        movq    %rax, -8(%rbp)
        xorl    %eax, %eax
        movl    -100(%rbp), %eax
        movl    %eax, -88(%rbp)
        movq    $0, -80(%rbp)
        movq    $0, -72(%rbp)
        movq    $0, -64(%rbp)
        movq    $0, -56(%rbp)
        movq    $0, -48(%rbp)
        movq    $0, -40(%rbp)
        movq    $0, -32(%rbp)
        movq    $0, -24(%rbp)
        movl    -100(%rbp), %eax
        movl    %eax, %edi
        call    str_len@PLT
        movl    %eax, -84(%rbp)
        movl    $0, -92(%rbp)
        jmp     .L_02
.L_03:
        movl    -100(%rbp), %eax
        cltq
        leaq    __mem(%rip), %rdx
        movzbl  (%rax,%rdx), %eax
        movb    %al, -93(%rbp)
        movl    -92(%rbp), %eax
        cltq
        movzbl  -93(%rbp), %edx
        movb    %dl, -80(%rbp,%rax)
        addl    $1, -100(%rbp)
        addl    $1, -92(%rbp)
.L_02:
        movl    -100(%rbp), %eax
        cltq
        leaq    __mem(%rip), %rdx
        movzbl  (%rax,%rdx), %eax
        testb   %al, %al
        jne     .L_03
        movl    -92(%rbp), %eax
        addl    $1, %eax
        cltq
        movb    $0, -80(%rbp,%rax)
        leaq    -80(%rbp), %rax
        movq    %rax, %rdi
        call    atoi@PLT
        movq    -8(%rbp), %rdx
        subq    %fs:40, %rdx
        je      .L_05
        call    __stack_chk_fail@PLT
.L_05:
        leave
        ret

	
        .text
        .section        .rodata
.FORMAT:
	.string "%d"
        .text
        .globl  int_to_str
        .type   int_to_str, @function
int_to_str:
        
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $64, %rsp
        movl    %edi, -52(%rbp)
        movq    %fs:40, %rax
        movq    %rax, -8(%rbp)
        xorl    %eax, %eax
        movl    -52(%rbp), %edx
        leaq    -32(%rbp), %rax
        leaq    .FORMAT(%rip), %rcx
        movq    %rcx, %rsi
        movq    %rax, %rdi
        movl    $0, %eax
        call    sprintf@PLT
        leaq    -32(%rbp), %rax
        movq    %rax, %rdi
        call    Str@PLT
        movl    %eax, -36(%rbp)
        movl    -36(%rbp), %eax
        movq    -8(%rbp), %rdx
        subq    %fs:40, %rdx
        je      .LEND_3
        call    __stack_chk_fail@PLT
.LEND_3:
        leave
        ret



        .globl  get_char_from_str
        .type   get_char_from_str, @function
get_char_from_str:
        
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $32, %rsp
        movl    %edi, -20(%rbp)
        movl    %esi, -24(%rbp)
        movq    %fs:40, %rax
        movq    %rax, -8(%rbp)
        xorl    %eax, %eax
        movl    -20(%rbp), %edx
        movl    -24(%rbp), %eax
        addl    %edx, %eax
        cltq
        leaq    __mem(%rip), %rdx
        movzbl  (%rax,%rdx), %eax
        movb    %al, -10(%rbp)
        leaq    -10(%rbp), %rax
        movq    %rax, %rdi
        call    Str@PLT
        movl    %eax, -16(%rbp)
        movl    -16(%rbp), %eax
        movq    -8(%rbp), %rdx
        subq    %fs:40, %rdx
        je      .Lgcfs3
        call    __stack_chk_fail@PLT
.Lgcfs3:
        leave
        ret
	.section	.rodata
.L_format:
	.string	"%s"
	.text
	.globl	input_str
	.type	input_str, @function
input_str:
.LFB8:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$160, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	leaq	-144(%rbp), %rax
	movq	%rax, %rsi
	leaq	.L_format(%rip), %rax
	movq	%rax, %rdi
	movl	$0, %eax
	call	__isoc99_scanf@PLT
	leaq	-144(%rbp), %rax
	movq	%rax, %rdi
	call	Str@PLT
	movl	%eax, -148(%rbp)
	movl	-148(%rbp), %eax
	movq	-8(%rbp), %rdx
	subq	%fs:40, %rdx
	je	.L_exit
	call	__stack_chk_fail@PLT
.L_exit:
	leave
	ret
	
	.globl	create_empty_str
	.type	create_empty_str, @function
create_empty_str:
	
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$16, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	movb	$0, -9(%rbp)
	leaq	-9(%rbp), %rax
	movq	%rax, %rdi
	call	Str@PLT
	movl	%eax, -16(%rbp)
	movl	-16(%rbp), %eax
	movq	-8(%rbp), %rdx
	subq	%fs:40, %rdx
	je	.L9_end
	call	__stack_chk_fail@PLT
.L9_end:
	leave
	ret

.globl	set
.type	set, @function
set:
	pushq %rbp
	movq %rsp, %rbp
	subq $128, %rsp  
	
	movq %rdi, -8(%rbp)		
	movq %rsi, -16(%rbp)	
	movq %rdx, -24(%rbp)
	movq -16(%rbp), %rax
	
	cltq
	
	leaq 0(,%rax,8), %rdx
	movq -8(%rbp), %rax
	addq %rax, %rdx	
	movq -24(%rbp),%rax
	movq %rax, (%rdx)

	movq $0, %rax
	movq %rbp, %rsp
	popq %rbp
	ret

.globl	get
.type	get, @function
get:
	pushq %rbp
	movq %rsp, %rbp
	subq $128, %rsp  

    movq %rdi,-8(%rbp)
    movq %rsi,-16(%rbp)
    movq -16(%rbp),%rax
    cltq   
    leaq 0(,%rax,8),%rdx
    movq -8(%rbp),%rax
    addq %rdx,%rax
	movq (%rax), %rax

	movq %rbp, %rsp
	popq %rbp
	ret
