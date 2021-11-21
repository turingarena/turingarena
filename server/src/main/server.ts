import { ApolloServer } from 'apollo-server-express';
import * as cors from 'cors';
import * as express from 'express';
import { Duration } from 'luxon';
import * as mime from 'mime-types';
import * as path from 'path';
import * as util from 'util';
import { PackageService } from '../core/archive/package-service';
import { LiveEvaluationService } from '../core/evaluate';
import { FileContent } from '../core/files/file-content';
import { mutationRoot } from '../core/mutation';
import { queryRoot } from '../core/query';
import { RemoteApiContext } from './api-context';
import { Config } from './config';
import { executableSchema } from './executable-schema';
import { InstanceContext } from './instance-context';
import { ServiceContext } from './service-context';

// Needed to make Docker exit correctly on CTRL-C
process.on('SIGINT', () => process.exit(0));

export function serve(config: Config) {
    const app = express();

    app.use(cors());
    console.log(config);

    const instanceContext = new InstanceContext(config);
    const serviceContext = new ServiceContext(instanceContext, [LiveEvaluationService, PackageService]);

    const server = new ApolloServer({
        schema: executableSchema(),
        context: async ({ req }) => {
            const token = req.headers.authorization ?? '';
            const nAuthParts = 2;
            const [authType, authPayload] = token.split(' ', nAuthParts);
            const user = authType === 'Bearer' ? await serviceContext.auth.auth(authPayload) : undefined;
            const apiCtx = new RemoteApiContext(serviceContext, user ?? undefined);

            return apiCtx;
        },
        rootValue: { ...mutationRoot, ...queryRoot },
        debug: true,
        playground: true,
        formatError: err => {
            console.warn(util.inspect(err, false, null, true /* enable colors */));

            return err;
        },
    });
    server.applyMiddleware({ app });

    app.use(express.static(config.webRoot));

    /**
     * Serve static files directly from the database.
     */
    app.get('/files/:contentId/:filename', async (req, res, next) => {
        try {
            const { contentId, filename } = req.params;
            const apiContext = new RemoteApiContext(serviceContext);
            const file = await apiContext
                .table(FileContent)
                .findOne({ where: { id: contentId }, attributes: ['content'] });
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

    // All other routes go to index.html
    app.get('*', (_, res) => {
        res.sendFile(path.join(config.webRoot, 'index.html'));
    });

    const callback = serviceContext.runAll();
    const server2 = app.listen(config.port, () => {
        console.log(`Server ready at: http://localhost:${config.port}${server.graphqlPath}`);
    });
    server2.on('close', callback);
}
