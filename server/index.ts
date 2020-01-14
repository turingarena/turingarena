import {
    ApolloServer,
    IResolvers,
    makeExecutableSchema,
} from 'apollo-server-express';
import * as express from 'express';
import { resolvers, schema } from './api';

const PORT = 3000;

const app = express();

const server = new ApolloServer({
    schema: makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    }),
    playground: true,
});

server.applyMiddleware({ app });

app.listen(PORT, () => {
    console.log(
        `Server ready at: http://localhost:${PORT}${server.graphqlPath}`,
    );
});
