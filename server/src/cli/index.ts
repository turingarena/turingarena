import * as commander from 'commander';
import { ApiContext } from '../api';
import { loadConfig } from '../config';
import { importContest } from './import';

const program = new commander.Command();

function serve() { }

function _export() { }

function show() { }

async function ctxFromConfig(configFile?: string): Promise<ApiContext> {
    const config = loadConfig(configFile);
    const context = new ApiContext(config);
    await context.sequelize.sync();

    return context;
}

program.name('turingarena').version('1.0');

program
    .command('serve')
    .description('start TuringArena server')
    .action(serve);

program
    .command('import [dir]')
    .description('import a contest')
    .option('-c, --config <path>', 'configuration file')
    .action(async (dir, opts) =>
        importContest(await ctxFromConfig(opts.config), dir),
    );

program
    .command('export')
    .description('export a contest')
    .action(_export);

program
    .command('show')
    .description('show information about a contest')
    .action(show);

program.parseAsync(process.argv).catch((e) => {
    process.emit('uncaughtException', e);
});
