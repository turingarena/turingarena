all: aplusb aplusb_driver

aplusb_stub.cpp: task.txt
	taskcc stub algorithm aplusb -o $@

aplusb_support.cpp: task.txt
	taskcc support algorithm aplusb -o $@

aplusb_driver_support.cpp: task.txt
	taskcc support driver -o $@

aplusb: aplusb_support.o

aplusb_driver: aplusb_driver_support.o

clean:
	rm -f aplusb_stub.cpp aplusb_support.cpp aplusb_driver_support.cpp aplusb_support.o aplusb aplusb_driver_support.o aplusb_driver
