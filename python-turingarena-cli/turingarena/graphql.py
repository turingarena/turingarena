import requests

from typing import List

from turingarena.submission import SubmissionFile


class GraphQlClient:
    endpoint: str

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def query(self, query: str, variables=()):
        request = dict(
            query=query,
            variables=variables,
        )

        response = requests.post(self.endpoint, json=request)

        return response.json()

    def init_db(self):
        return self.query("""
            mutation {
               initDb {
                  ok
               }
            }
        """)

    def show_contest(self):
        return self.query("""
        query {
            contest {
               startTime
               endTime
               problems {
                  name
               },
               users {
                  id,
                  displayName,
                  isAdmin,
                }
            }
        }
        """)

    def create_contest(self, args: dict):
        return self.query("""
        mutation($contest: ContestUpdateInput!, $users: [UserInput!]!, $problems: [ProblemInput!]!) {
            updateContest(input: $contest) {
                ok
            },
            addUsers(inputs: $users) {
                ok
            },
            addProblems(inputs: $problems) {
                ok
            }
        }
        """, args)

    def submissions(self):
        return self.query("""
        query {
            contest {
                submissions {
                    id,
                    userId,
                    createdAt,
                    problem {
                        name
                    },
                    evaluation {
                        id,
                        status,
                    },
                    files {
                        fieldId,
                        typeId,
                        name,
                        content {
                            base64
                        },
                    }
                }
            }
        }
        """)

    def submit(self, user: str, problem: str, files: List[SubmissionFile]):
        args = dict(
            user=user,
            problem=problem,
            files=list(map(lambda f: f.to_graphql(), files))
        )
        return self.query("""
        mutation ($user: String!, $problem: String!, $files: [FileInput!]!) {
            submit(userId: $user,problemName: $problem,files: $files){
                id
            }
        }        
        """, args)
