# Contest file format 

This is the specification of the contest description. A contest is a directory that is structured this way:
```
/
+-- turingarena.yaml
+-- task1/
+-- task2/
+-- task3/
|     ...
+-- files/
      +-- home.html
      +-- img/
      +-- ...
```

All the directories except the one starting with `_` or `.`, and the `files/` directory, 
are treated as task, whose ID is the directory name. Thus to disable a task you can rename the directory as `_task/`

The `turingarena.yaml` file is structured this way:
```yaml
title: Very big contest
start: 2020-01-05T14:00:00Z # if not present the contest starts immediately
end: 2020-01-05T18:00:00Z   # if not present the contest runs forever
users:
  - id: alerighi
    name: Alessandro Righi
    token: xyejhfdyyujd
    role: admin # optional
  - id: cairomassimo
    name: Massimo Cairo
    token: jfkldyyjjkjk
```

The ID of the contest is the name of the directory in which the `turingarena.yaml` is located. 
To change the contest id, simply rename the directory. 

This file is named `turingarena.yaml` to let you share a contest directory with a CMS contest, making it 
compatible with both systems. A `contest.yaml` file is simply ignored. 

To convert a Italy YAML `contest.yaml` file to a TuringArena `turingarena.yaml` you can use the command:
```
turingarena convert
```
inside the contest directory. A new file `turingarena.yaml` will be created.  

To import a task, simply launch:
```
turingarena import [--fresh]
```
from inside the contest directory. TuringArena will search for a `turingarena.yaml` in the parents directory 
if not found, so you can launch the command also from inside a task directory. 

The `improt` command will update the if it already exists,
unless the `--fresh` option is specified: in that case the contest will be dropped and reimported from scratch, deleting
all submissions and data. 

To export a contest, to port it to other machines, you can use the command:
```
turingarena export <contest id> [--submissions]
``` 

The contest will be exported to a directory named with the ID of the contest.
The option `--submissions` will also export the submissions in the directory `_submissions/`. 

To delete a contest permanently, use the command:
```
turingarena drop <contest id>
```
