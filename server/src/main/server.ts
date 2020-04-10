import { ApolloServer } from 'apollo-server-express';
import * as express from 'express';
import * as fs from 'fs';
import { Duration } from 'luxon';
import * as mime from 'mime-types';
import * as path from 'path';
import * as util from 'util';
import { FileContent } from '../core/file-content';
import { ApiContext } from './api-context';
import { Config } from './config';
import { ModelRoot } from './model-root';

const findWebRoot = () => {
    let dir = __dirname;

    while (!fs.existsSync(path.join(dir, 'web'))) {
        dir = path.resolve(dir, '../');
    }

    return path.join(dir, 'web/dist/turingarena-web');
};

const webRoot = findWebRoot();

// Needed to make Docker exit correctly on CTRL-C
process.on('SIGINT', () => process.exit(0));

export function serve(config: Config) {
    const app = express();

    console.log(config);

    const root = new ModelRoot(config);

    const server = new ApolloServer({
        schema: ApiContext.executableSchema,
        context: async ({ req }) => {
            const token = req.headers.authorization ?? '';
            const nAuthParts = 2;
            const [authType, authPayload] = token.split(' ', nAuthParts);
            const user = authType === 'Bearer' ? await root.authService.auth(authPayload) : undefined;
            const api = new ApiContext(root, user ?? undefined);

            return api;
        },
        rootValue: root,
        debug: true,
        playground: true,
        formatError: err => {
            console.warn(util.inspect(err, false, null, true /* enable colors */));

            return err;
        },
    });
    server.applyMiddleware({ app });

    app.use(express.static(webRoot));

    app.get('/', (_, res) => {
        res.sendFile(path.join(webRoot, 'index.html'));
    });

    /**
     * Serve static files directly from the database.
     */
    app.get('/files/:contentId/:filename', async (req, res, next) => {
        try {
            const { contentId, filename } = req.params;
            const file = await root.table(FileContent).findOne({ where: { id: contentId }, attributes: ['content'] });
            const contentType = mime.lookup(filename);

            if (file === null) {
                next();

                return;
            }

            // FIXME: serving untrusted content, investigate security issues

            res.contentType(contentType !== false ? contentType : 'text/plain');
            res.header('Content-Security-Policy', `script-src 'none'; object-src 'none'`); // Should disallow script execution (?)
            res.header('Content-Disposition', `inline; filename=${JSON.stringify(filename.toString())}`);
            res.header(
                'Cache-Control',
                `private, immutable, max-age=${Duration.fromObject({ years: 1 })
                    .as('seconds')
                    .toString()}`,
            );
            res.send(file.content);
        } catch (e) {
            next(e);
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
