import { ApolloServer } from 'apollo-server-express';
import * as express from 'express';
import { FileContent } from '../core/file-content';
import { ApiContext } from './api-context';
import { Config } from './config';
import { ModelRoot } from './model-root';

export function serve(config: Config) {
    const app = express();

    console.log(config);

    const modelRoot = new ModelRoot(config);
    const api = new ApiContext(modelRoot);

    const server = new ApolloServer({
        schema: api.executableSchema,
        context: api,
        rootValue: api.modelRoot,
        debug: true,
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
    app.get('/files/:hash/*', async ({ params: { hash } }, res, next) => {
        const file = await modelRoot.table(FileContent).findOne({ where: { hash } });
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
        console.log(`Server ready at: http://localhost:${config.port}${server.graphqlPath}`);
    });
}
