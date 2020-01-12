import { ApolloServer, IResolvers, makeExecutableSchema } from 'apollo-server-express';
import * as express from 'express';

import { typeDefs } from './graphql';
import { resolvers } from './resolvers';

const PORT = 3000;

const app = express();

const schema = makeExecutableSchema({
  typeDefs,
  resolvers: resolvers as IResolvers,
});

const server = new ApolloServer({
  schema,
  playground: true,
});

server.applyMiddleware({ app });

app.listen(PORT, () => {
  console.log(`Server ready at: http://localhost:${PORT}${server.graphqlPath}`);
});
