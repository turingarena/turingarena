docker run \
    --name turingarena \
    --rm \
    --read-only \
    --tmpfs /run/turingarena:exec,mode=1777 \
    --tmpfs /tmp:exec,mode=1777 \
    --volume $PWD:/usr/local/turingarena/:ro \
    --publish 127.0.0.1:20122:22 \
    turingarena/turingarena:${1:-latest} \
    socat TCP-LISTEN:22,fork EXEC:"/usr/sbin/sshd -i -e -o PermitEmptyPasswords=yes -o Protocol=2",nofork
