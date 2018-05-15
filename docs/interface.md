# TuringArena Interface Definition Language

The interface file is composed by two sections:
 
- function and procedure declarations
- main block 

They must occur in the above order.

## Comments

In the whole interface you can insert comment with the C++ syntax: 

```C
// single line comment

/* 
 * multiline comment 
 */
```

## Types
In TuringArena we have only 2 data types:
- *scalar* types, that are signed integer types
- *array* types, that are k-dimensional arrays of scalar types

## Function and procedure declarations

The first section of the interface declares the functions and procedures that an algorithm needs to implement.
Every interface must declare at least one function or procedure.
Each function or procedure has a *name* (unique in the interface) and a *type*.

As in Pascal, the difference between a function and a procedure is that a function returns a value while the procedure don't. 

A function or a procedure can have callbacks, functions that who writes that function can call to comunicate with the problem. A callback could be a function or a procedure, that can take only scalar parameters (no arrays). 


### Syntax

The syntax of a function or procedure delaration is the following:
- either `procedure` or `function` keyword
- a *name*, that must be a valid identifier (as the notion of identifier of most programming languages)
- open round bracket `(`
- zero or more parameters declarations, that are composed by:
   * the parameter *name*, that must be a valid identifier
   * optionally, a set of `[]` for each dimension of the array (like C)
- close round bracket `)`
- either one of the following options:
   * if the function does not accept callbacks, `;`
   * otherwise, a callback definition block that is composed of:
       * the `callback` keyword, followed by open brace `{
       * one or more function or procedure declarations (with the same syntax already described)
       * closed brace `}`

### Examples
Valid declarations:
```C
function sum(a, b); 
procedure init(); 
procedure init_graph(N, d[], adj[][]); // d is a simple array, adj is a multidimensional array (a matrix) 
function with_callback(a) callbacks {
    function func(a, b);
    procedure func2(d);
    procedure not_very_useful());
}
```

Invalid declarations:
```C
procedure invalid_callback() {
    procedure callback(a[])); // error: array parameters not allowed in callback
}
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
read var1, var2, array[i], matrix[i][j];
```
Variables are automatically declared as you read them, and shouldn't been already declared.  
For array variables, they must be read only inside a for loop and they are declared as big as the corrisponding for index variable range. Every variable that you read should be passed to a function. 

### Write statement 
The write statement lets you write one or more variables to the problem, and has the following syntax:
```C
write var1, var2, array[i], matrix[i][j]; 
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
The call statement lets you call a function or a procedure, and it's composed by:
- the `call` keyword
- only if you are calling a function, a lvalue expression followed by the `=` sign
- the function or procedure name
- a list of parameters, between round brackets 
- if the funzion accepts callbacks, a callback definition block that it's composed of:
    * the `callback` keyword followed by open brace `{`
    * one or more function or procedure implementation
    * closing brace `}`
    
    
Note: if the funzion takes callbacks but you don't implement all the callbacks (or none of them), they are assumed as thefault, that is a function or procedure that writes all it's arguments, and if it's a function reads the return value and returns it. 


Examples:
``` C
call func(a, b); // void function
call result = func(a, b); // save return value into result
call func(a, b) callbacks {
    function sum(a, b) { // callback definition
        return a + b;
    }
    procedure cb(int a) {
        write a;
    }
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
Unlike C, switch cases does not falltrough. Case labels should be int literals, and you could put more labels to a case separated by a comma. 
The switch expression should be an integer expression. There is no default case. 

