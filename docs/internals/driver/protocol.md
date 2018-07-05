# Driver protocol 

This file describe the specification of the comunication protocol between the driver and the evaluator. 

## Enviroment variables

The drivers comunitate to the evaluator process the parameters with the use of enviroment variables. 
The variables defined are the following:
- `TURINGARENA_SANDBOX_DIR` the temporary directory where the driver runs
- `SUBMISSION_FILE_$name` the path of the file $name ($name must be uppercase). For example, SUBMISSION_FILE_SOURCE is the source file. 
- `EVALUATION_DATA_BEGIN`/`EVALUATION_DATA_END` variables that contains a unique token that must be printed before/after the evaluation data. 

## Starting the process 
To start the process, you must comunicate to the driver some parameters in this exact order, to do so you must write in these pipes:
- `$TURINGARENA_SANDBOX_DIR/language_name.pipe` the name of the language of the solution (if empty, the language is automatically determinated by the submitted file extension)
- `$TURINGARENA_SANDBOX_DIR/source_path.pipe` the path of the submitted source file
- `$TURINGARENA_SANDBOX_DIR/interface_path.pipe` the path of the interface.txt

Remember to close the pipes after writing to them, so the stream is flushed. 

Then the driver procedes to compile and start the program, and gives you the path of the sandbox process dir. 
You must read this variable from the pipe $TURINGARENA_SANDBOX_DIR/sandbox_process_dir.pipe. 

In the sandbox_process_dir, you finnally have the two pipes that let's you send commands to the driver and recieve responses. 
These pipes are:
- `$sandbox_process_dir/driver_downward.pipe` that let's you send commands to the driver
- `$sandbox_process_dir/driver_upward.pipe` that let's you recieve the response from the driver

You can send the following requests to the driver:
- `CALL` call a function
- `WAIT` wait for a function to terminate and returns the resource usage data 
- `EXIT` terminates the proces
- `CALLBACK RETURN` tell the driver the return value of a callback
- `CHECKPOINT` checkpoint request 

It's important to remember to call `EXIT` to terminate the program. 


### Reading error status 
Before sending any request to the driver, is absolutely important to first read the error status. The error status is a single
integer that you read from the upward pipe. If it's `0` it means no errors, if it's `1` it means that there was an error. 

The syntax of the error messages is the following:
- time usage of the process (int)
- memory usage of the process (float)
- error message (string)

### CALL request
To do a call you must write to the downward pipes the following parameters, followed by a newline `\n`:
- the string `request`
- the string `call`
- the name of the function to call
- the numbers of parameters, as an integer
- for each function argument, the argument in this way:
	* if the argument is an integer, you write `0` and then on a new line the parameter value
	* if the argument is an array, you write `1`, then you write the array length, then you write recursively every value of the array
- the integer `1` if the call has a return value (is a function), the integer `0` if the call does not return (is a procedure)
- the number of callbacks that the call accepts
- for each callback, the number of its arguments 

Then remember to flush the stream, and the driver procedes to call the function. You then begin to listen to the upward_pipe for the response. 

The response consists of only integer parameters, in this order:
- an integer `0` if the function doesn't call callbackes, the integer `1` if it does, followed by the callback index and it's parameters (in wich format ?)
- the status, that is `0` if the execution completed succesfully, `1` in case of errors
- in case of an error, the error status (in wich format ?)
- if the call has a return value, the return value

#### Example
Let's take for example the call `sum(4, 5)`, this is the request that must be written on the downward_pipe
```
requet 
call 
sum
2 # two arguments
0 # first argument scalar
4 # value
0 # second argument also scalar
5 # value
1 # has a return value
0 # doesn't have callbacks 
```

And you should get this response
```
0 # no callbacks
0 # execute successfully 
9 # return value 
```

### WAIT request
To do a wait request, you should write on the downward_pipe the following parameters:
- the string `wait`
- the integer `1` if you want to kill the process, the integer `0` if not

Then, you read on the upward pipe the following parameters:
- the CPU usage of the process in seconds, as a float
- the memory usage of the process, in bytes

#### Example
This is the request
```
wait
0 # do not kill
``` 
And this the response
```
0.012 # CPU usage
10000 # memory usage
```

### EXIT request
This request terminates the process correctely.

You should allways send an EXIT request when you finished calling functions. After an EXIT request, you can't send other requests. 

To do an exit request, you should write on the downward_pipe the following:
- the string `request`
- the string `exit`

Obviously you don't get any response back. 

#### Example 
```
request
exit
``` 

### CALLBACK RETURN request
This request tells the driver that a callback has returned and the eventual return value

You must write to the `downward_pipe` the following lines:
- the string `request`
- the string `callback_return`
- the integer `1` if the callback has a return value, `0` if not
- it has return value, the return value

#### Example
```
request
callback_return
1 # has return value = True
42 # value
```

### CHECKPOINT REQUEST
This request serves to syncronize to a `checkpoint` instruction in the solution.  

Syntax:
- the string `request`
- the string `checkpoint`

#### Example
```
request
checkpoint
```

## TODO
- syntax of error messages is not documented
- syntax of the callback request is not documented
