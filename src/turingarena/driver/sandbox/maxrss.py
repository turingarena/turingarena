import os
import resource
import signal
import time


def main():
    a = [None] * 1000000

    print("PARENT:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    pid = os.fork()

    del a

    if pid == 0:
        pid = os.getpid()
        print("HWM", "BEFORE getrusage:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        with open(f"/proc/{pid}/status") as f:
            print(f.read())
        time.sleep(1)
        print("HWM", "AFTER getrusage:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        with open(f"/proc/{pid}/status") as f:
            print(f.read())
    else:
        os.kill(pid, signal.SIGSTOP)
        print("HWM", "WAIT stopped before", os.wait4(pid, os.WUNTRACED)[2].ru_maxrss)
        with open(f"/proc/{pid}/status") as f:
            print(f.read())
        os.kill(pid, signal.SIGCONT)

        time.sleep(0.5)

        os.system(f"echo 5 > /proc/{pid}/clear_refs")

        os.kill(pid, signal.SIGSTOP)
        print("HWM", "WAIT stopped after", os.wait4(pid, os.WUNTRACED)[2].ru_maxrss)
        with open(f"/proc/{pid}/status") as f:
            print(f.read())
        os.kill(pid, signal.SIGCONT)

        print("HWM", "WAIT", os.wait4(pid, 0)[2].ru_maxrss)


if __name__ == '__main__':
    main()
