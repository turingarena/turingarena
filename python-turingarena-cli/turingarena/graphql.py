import sys

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from requests import HTTPError


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
