import os
import subprocess


def serve_sshd(name):
    os.makedirs(f"/var/run/turingarena/{name}", exist_ok=True)
    subprocess.run(
        [
            "socat",
            f"UNIX-LISTEN:/var/run/turingarena/{name}/sshd.sock,fork,mode=0666",
            f"EXEC:/usr/sbin/sshd -i -e -o PermitEmptyPasswords=yes -o PermitRootLogin=yes -o Protocol=2",
        ]
    )
