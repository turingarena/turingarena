Interface syntax
================

The interface files is composed by two sections, that should be present in the following order: 
- function declarations
- main block 

In the whole interface you can insert comment with the C++ syntax: 
```C
// single line comment

/* 
 * multiline comment 
 */
```

Function delarations
---------------------

In this section you declare the functions that who writes the solution needs to implement. 
Every problem must declare at least one function. 
The syntax of function declaration is similary to the C syntax, with some minor differences:
- the only return types permitted are `int` and `void`. Function cannot return arrays
- if you need to pass an array to a function you put squared brackets after the variable name, without specifying the size. You cannot use pointer syntax to pass arrays
- functions that don't take parameters should be declared with an empty parameters list, `void` in the parameters list is not allowed
- functions can take callbacks as parameters, with the usual C syntax.
- callbacks declaration must specify the parameters names, not only their type
- callbacks must only take scalar (`int`) parameters and return only `int` or `void`, they are not allowed to take arrays or other functions as parameters

### Examples
Valid declarations:
```C
int sum(int a, int b);
void init(); 
int with_callback(int a, int func(int a, int b), void func2(int d), void not_very_useful());
void init_graph(int N, int adj[][]); 
```

Invalid declarations:
```C
int[] returns_array(); // must return only scalars 
void init(void); // void not allowed, declare as void init();
int invalid_callback(void callback(int a[])); // array parameters not allowed in callback
int invalid_callback2(int sum(int, int)); // must specify callback argument name
```

Main body
---------

The main body is the code that will be translated to the skeleton of the languages in wich the solution is written. 
It must read variables, call functions, and write back the result. 

The main body should be declared after all function declaration and with the following syntax:
```C
// one or more function declaration

main {
  // statements
}
```

### Read statemenent 
The read setaments lets you read one or more variables from the problem, and has the following syntax:
```C 
read var1, var2, array[i], matrix[i][j], ...;
```
Variables are automatically declared as you read them, and shouldn't been already declared.  
For array variables, they must be read only inside a for loop and they are declared as big as the corrisponding for index variable range. Every variable that you read should be passed to a function. 

### Write statement 
The write statement lets you write one or more variables to the problem, and has the following syntax:
```C
write var1, var2, array[i], matrix[i][j], ...; 
```
You must write only variables that are the result of a function call. 

### Checkpoint statement
Checkpoint statement inserts a checkpoint inside the interface, in practice it writes a 1 to the problem. It has the following syntax:
```C
checkpoint; 
```

### Exit statement
Exit statement terminates the execution of the interface, and has the following syntax:
```C
exit; 
```

### Call statement 
The call statement lets you call a function, and has the following syntax:
``` C
call func(a, b); // void function
call result = func(a, b); // save return value into result
``` 

### Callback declaration syntax
In the interface you can declare callback, that you can pass to function. The declaration syntax is similar to the function declaration 
syntax of the C language, with the exception the you must take only `int` parameters and return either `int` or `void`. 
Callbacks can use variables defined in the scope where you declare the callback. 
Example:
```C
int func(int a, int b) {
  // do something
}
```

It's common in a callback declaration to write all the parameter and read back the return value, for this common use case you can omit the 
function body and put the default keyword, like this:
```C
int callback(int a, int b) default;
``` 
This is the equivalent to:
```C
int callback(int a, int b) {
  write a, b; 
  read result;
  return result;
}
``` 

### For statement
For loop lets you iterate in a range, and has the following syntax:
```C
for index to range {
  // statements
}
```
This is the equivalent of a for loop in the C style:
```C 
for (int index = 0; index < range; index++)
```

### Loop statement
The loop statement perform an infinite loop, and has the following syntax:
```C
loop {
  // statements 
}
```
This is the equivalent of a `while (true)` in the C language. A loop staement can contain `continue` or `break` statements, 
that have the usual meaning. You shouldn't write infinite loops, a loop must contain either a `break` or `exit` statement. 

### If statement 
The if statement has the following syntax:
```C
if condition {
  // statements
} else {
  // statements 
}
```
Condition should be a boolean expression, such as a comparison expression. The else body could be omitted as in other languages. 
Brackets are obbligatory even if the body contains a single statement.

### Switch statement 
Switch statement has the following syntax:
```C
switch expression {
  case 1 {
    // statements
  }
  case 2, 3 {
    // statements
  }
  ...
}
```
Unline C, switch cases does not falltrough. Case labels should be int litterals, and you could put more labels to a case separated by a comma. 
The switch xpression should be an integer expression. There is no default case. 

