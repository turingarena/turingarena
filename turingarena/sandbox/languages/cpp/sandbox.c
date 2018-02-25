/* 
 * Simple Linux sandbox program that uses seccomp to deny all system calls to a program,
 * except those listed in filter_instructions.
 * 
 * How to use: 
 *     - compile with `gcc -c sandbox.c`
 *     - link to executable to sandbox `gcc sandbox.o program.o` 
 *     WARNING: sandbox.o must be linked before other object files to guarantee 
 *       that no code is executed before the sandbox initialization function!
 */

#if !defined(__x86_64__) || !defined(__linux__)
#error Unsupported platform
#endif

#include <sys/prctl.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <asm/unistd.h>
#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>

#define DEBUG(message) fprintf(stderr, "DEBUG: %s \n", message)
#define CAT(a, b) a ## b 
#define ALLOW(syscall) \
	BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, CAT(__NR_,syscall), 0, 1), \
	BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)

/* 
 * Instructions of the BPF syscall filter program  
 */
static struct sock_filter filter_instructions[] = {
	/* Ensure the syscall arch convention is x86_64, so you can't make call with old 32bit ABI (int 0x80/sysenter) */
	BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
	BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
	BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRAP),

	/* Load the syscall number for checking */
	BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),

	/* Allow exit */
	ALLOW(exit),
	ALLOW(exit_group),

	/* Allow memory allocation */
	ALLOW(brk),
	ALLOW(mmap),
	ALLOW(mremap),
	ALLOW(munmap),

	/* Allow read/write */
	ALLOW(read),
	ALLOW(write),
	ALLOW(lseek),
	ALLOW(fstat),

	BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRAP)
};

/* 
 * Struct that contains the BPF program to filter syscalls 
 */
static struct sock_fprog seccomp_filter_program = {
	.len = sizeof(filter_instructions) / sizeof(filter_instructions[0]),
	.filter = filter_instructions,
};

/*
 * Initialization function that is called to initialize the sandbox by the libc
 */
static void sandbox_init(void) 
{
	DEBUG("Initializing sandbox");

	if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
		perror("Error calling prctl(PR_SET_O_NEW_PRIVS, 1)");
		_Exit(EXIT_FAILURE);
	}

	if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &seccomp_filter_program) == -1) {
		perror("Error calling prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &seccomp_filter_program)");
		_Exit(EXIT_FAILURE);
	}

	DEBUG("Sandbox initialized");
}

/* 
 * Put function pointer in .preinit_array to execute before any other initialization function.
 * .preinit_array is a section in the ELF header that contains the pointers to functions that
 * are called in order by the libc on initialization, before any other constructor function. 
 */
__attribute__((section(".preinit_array"), used)) static void (*preinit_fun)(void) = sandbox_init;
