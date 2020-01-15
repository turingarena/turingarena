import { ApolloServer } from 'apollo-server-express';
import * as express from 'express';
import { ApiContext, schema } from './api';

const PORT = 3000;

const app = express();

const server = new ApolloServer({
    typeDefs: schema,
    executor: (req) => new ApiContext().execute(req),
    playground: true,
});

server.applyMiddleware({ app });

app.listen(PORT, () => {
    console.log(
        `Server ready at: http://localhost:${PORT}${server.graphqlPath}`,
    );
});
