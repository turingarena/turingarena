import { ApolloServer } from 'apollo-server-express';
import * as express from 'express';
import { ApiContext, schema } from './api';

const PORT = 3000;

const app = express();

const context = new ApiContext();

context.sequelize.sync().then(() => {
    context.db.File.create('ciao', 'ciao.txt', 'text/plain').then(console.log);
});

const server = new ApolloServer({
    typeDefs: schema,
    executor: (req) => context.execute(req),
    playground: true,
});

server.applyMiddleware({ app });

/**
 * Serve static files directly from the database.
 */
app.get('/files/:hash/*', async (req, res, next) => {
   const hash = req.params.hash;
   const file = await context.db.File.findOne({ where: { hash }});
   if (file === null) {
       return next();
   }
   res.contentType(file.type);
   res.send(file.content);
});

/**
 * Add a file to the server
 */
app.post('/files/:name', async (req, res) => {
    // TODO
});

app.listen(PORT, () => {
    console.log(
        `Server ready at: http://localhost:${PORT}${server.graphqlPath}`,
    );
});
