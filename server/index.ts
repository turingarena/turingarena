import * as express from 'express';
import * as bodyParser from 'body-parser';
import { ApolloServer, makeExecutableSchema, gql } from 'apollo-server-express';

const PORT = 3000;

const app = express();

const schema = makeExecutableSchema({
  typeDefs: gql`
    type Query {
      a: String!
    }
  `,
  resolvers: {
    Query: {
      a: () => `a string`,
    },
  },
})

const server = new ApolloServer({
  schema,
  playground: true,
});

server.applyMiddleware({ app })

app.listen(PORT, () => {
  console.log(`Server ready at: http://localhost:${PORT}${server.graphqlPath}`);
});
