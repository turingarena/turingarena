# test program for C sandbox 

import os 

tests = [
	("test_constructor", False),
	("test_c_valid", True),
	("test_c_invalid", False),
	("test_cpp_valid", True),
	("test_cpp_invalid", False)
]

def execute(test: str, valid: bool):
	print("Testing " + test)
	retval = os.system("test/" + test)
	if valid:
		assert retval == 0
	else:
		assert retval != 0

def test_sandbox():
	assert os.system("make clean") == 0
	assert os.system("make tests") == 0
	for exe, valid in tests:
		execute(exe, valid) 
	assert os.system("make clean_tests") == 0
	