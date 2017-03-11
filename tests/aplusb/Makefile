all: aplusb

aplusb.cpp: task.txt
	taskcc stub algorithm aplusb -o $@

aplusb_support.cpp: task.txt
	taskcc support algorithm aplusb -o $@

aplusb: aplusb_support.o
