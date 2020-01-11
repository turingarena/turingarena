# RFC of problem material format

This is a specification of the interface between TA and the evaluation backend (i.e. Task Maker)

### Problem format

TuringArena will ask the backend the metadata of the task, specifying an option like `--task-info`. 
The backend should output to the standard output the description of the task in the following format:
```json
{
  "version": 1.0,
  "type": "ioi-task",
  "name": "short-name",
  "title": "long name of the task",
  "limits": {
    "time": 1,
    "memory": 256
  },
  "scoring": {
    "max-score": 100,
    "subtasks": [
      {
        "max-score": 10,
        "testcases": 2,
      },
      {
        "max-score": 90,
        "testcases": 10,
      }
    ]
  },
  "statements": [
    {
      "language": "it_IT",
      "path": "statement/italian.pdf",
      "content-type": "application/pdf"
    },
    {
      "language": "en_US",
      "path": "statement/english.md",
      "content-type": "text/markdown"
    }
  ],
  "attachements": [
    {
      "name": "input0.txt",
      "description": "Example of input",
      "content-type": "text/plain",
      "path": "att/input0.txt"
    }
  ]
}

```

