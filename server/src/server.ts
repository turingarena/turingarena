import { ApolloServer } from 'apollo-server-express';
import * as express from 'express';
import { ApiContext, schema } from './api';
import { Config } from './config';

export function serve(config: Config) {
    const app = express();

    console.log(config);

    const context = new ApiContext(config);

    context.sequelize.sync().then(() => {
        context.db.File.create({
            content: 'ciao',
            fileName: 'ciao.txt',
            type: 'text/plain',
        });
    });

    const server = new ApolloServer({
        typeDefs: schema,
        executor: req => context.execute(req),
        playground: true,
        formatError: err => {
            console.warn(err);

            return err;
        },
    });
    server.applyMiddleware({ app });

    /**
     * Serve static files directly from the database.
     */
    app.get('/files/:hash/*', async (req, res, next) => {
        const hash = req.params.hash;
        const file = await context.db.File.findOne({ where: { hash } });
        if (file === null) next();
        else {
            res.contentType(file.type);
            res.send(file.content);
        }
    });

    /**
     * Add a file to the server
     */
    app.post('/files/:name', (req, res) => {
        // TODO
    });

    app.listen(config.port, () => {
        console.log(
            `Server ready at: http://localhost:${config.port}${server.graphqlPath}`,
        );
    });
}
