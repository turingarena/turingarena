#!/usr/bin/env bash

for i in $(seq 10) ; do

    echo -n > $TURINGARENA_SANDBOX_DIR/language_name.pipe
    echo -n :$SUBMISSION_FILE_SOURCE > $TURINGARENA_SANDBOX_DIR/source_name.pipe
    echo -n ":interface.txt" > $TURINGARENA_SANDBOX_DIR/interface_name.pipe
    read sandbox_process_dir < $TURINGARENA_SANDBOX_DIR/sandbox_process_dir.pipe

    a=$((RANDOM%1000))
    b=$((RANDOM%1000))

    {
        echo request
        echo call
        echo sum
        echo 2 # nargs
        echo 0 # scalar
        echo $a
        echo 0 # scalar
        echo $b
        echo 1 # 0=procedure, 1=function
        echo 0 # callbacks

        read c

        echo wait
        echo 0 # do not kill it (FIXME)

        read time_usage
        read memory_usage
        read status

        echo request
        echo exit
    } >$sandbox_process_dir/driver_downward.pipe  <$sandbox_process_dir/driver_upward.pipe

    echo -n "$a + $b --> $c"

    if (( a + b == c )) ; then
        echo " (correct)"
    else
        echo " (wrong)"
        wrong=1
    fi

done

if (( wrong == 1 )) ; then
    echo
    echo $EVALUATION_DATA_BEGIN
    jq -nc '{"goals": {"correct": false}}'
    echo $EVALUATION_DATA_END
else
    echo
    echo $EVALUATION_DATA_BEGIN
    jq -nc '{"goals": {"correct": true}}'
    echo $EVALUATION_DATA_END
fi