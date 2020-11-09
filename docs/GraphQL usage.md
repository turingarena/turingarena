# GraphQL Usage

## Fragment used

 ### `Text`
```
variant
```

 ### `TopBar`
 ```
title {
      ...Text
    }
    user {
      id
      name
    }
```

### `MediaInline`
```
variant {
      name
      type
      url
    }
```


 ### `ContestView`
 ```
contest {
      id
      title {
        ...Text
      }
      statement {
        ...MediaInline
      }
    }

    problemSetView {
      assignmentViews {
        assignment {
          id
          problem {
            id
            name
            statement {
              ...MediaInline
            }
          }
        }
        ...ContestProblemAssignmentViewAside
      }
    }

    ...ContestViewAside
  }
```


## `contest-problem-assignment-user-tackling-aside.tsx`
```
canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }
    }

    ...ContestProblemAssignmentUserTacklingSubmitModal
    ...ContestProblemAssignmentUserTacklingSubmissionList
}
```

## `contest-problem-assignment-user-tackling-submission-list.tsx`
```

```

## ``
```

```

## ``
```

```

## ``
```

```

## `MainView.ts`
```
...TopBar
contestView {
    ...ContestView
}
```

