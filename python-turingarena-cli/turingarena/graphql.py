import sys

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from requests import HTTPError
from typing import List

from turingarena.submission import SubmissionFile


class GraphQlClient:
    client: Client

    def __init__(self, endpoint: str):
        transport = RequestsHTTPTransport(endpoint + "/graphql", use_json=True)
        self.client = Client(transport=transport)

    def execute(self, query, *args, **kwargs):
        try:
            return self.client.execute(query, *args, **kwargs)
        except HTTPError as e:
            print(e.response.json(), file=sys.stderr)
            raise e

    def init_db(self):
        return self.execute(gql("""
            mutation {
               initDb {
                  ok
               }
            }
        """))

    def show_contest(self):
        return self.execute(gql("""
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
        """))

    def create_contest(self, args: dict):
        return self.execute(gql("""
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
        """), args)

    def submissions(self):
        return self.execute(gql("""
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
        """))

    def submit(self, user: str, problem: str, files: List[SubmissionFile]):
        args = dict(
            user=user,
            problem=problem,
            files=list(map(lambda f: f.to_graphql(), files))
        )
        return self.execute(gql("""
        mutation ($user: String!, $problem: String!, $files: [FileInput!]!) {
            submit(userId: $user,problemName: $problem,files: $files){
                id
            }
        }        
        """), args)
