require 'fiddle/import'

module Seccomp
  extend Fiddle::Importer
  dlload "libseccomp.so.2"
  extern "void* seccomp_init(int)"
  extern "int seccomp_rule_add(void*, int, int, int)"
  extern "int seccomp_load(void*)"
  extern "int seccomp_syscall_resolve_name(void*)"

  SCMP_ACT_KILL     = 0x00000000
  SCMP_ACT_TRAP     = 0x00030000
  SCMP_ACT_ERRNO_0  = 0x00050000
  SCMP_ACT_ALLOW    = 0x7fff0000
end

def init_sandbox()
    ctx = Seccomp.seccomp_init(Seccomp::SCMP_ACT_TRAP)
    ret = 0
    syscalls = [
        "read", "write", "readv", "writev",  # base I/O
        "lseek", "ioctl", "fstat",
        "exit", "exit_group", "rt_sigreturn",
        "mmap", "munmap", "mremap", "brk",
        "execve",
        "arch_prctl", "uname", "set_tid_address",
        "time", "futex", "close", "getpid"
    ]
    syscalls.each do |s|
        ret |= Seccomp::seccomp_rule_add(ctx, Seccomp::SCMP_ACT_ALLOW, Seccomp::seccomp_syscall_resolve_name(s), 0)
    end

    ret |= Seccomp::seccomp_load(ctx)
    fail "Something went wrong." unless ret == 0
end

def main()
    load ARGV[0]
    init_sandbox

    # From here every system call that is not allowed will result in an Exception

    main
end

if __FILE__ == $0
    main
end
