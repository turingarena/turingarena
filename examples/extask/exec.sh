#!/bin/bash

g++ solution_support.cpp alien.cpp -o solution
g++ driver_stages_support.cpp driver.cpp --std=c++11 -o driver

mkfifo foo
cat foo |

while read line; do
    echo -e "\e[01;31m  DRIVER:\t$line\e[0m"  1>&2
    echo $line
done |

./solution | 

while read line; do
    echo -e "\e[01;33mSOLUTION:\t$line\e[0m" 1>&2
    echo $line
done | 

./driver 2>&1 > foo | 
while read line; do
    echo -e "\e[01;32mDRIVER INFO:\t$line\e[0m" 1>&2
done 


