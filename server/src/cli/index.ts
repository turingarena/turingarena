#!/usr/bin/env node

import * as commander from 'commander';
import { ApiContext, ApiEnvironment, LocalApiContext } from '../main/api-context';
import { loadConfig } from '../main/config';
import { serve } from '../main/server';
import { ContestImportApi } from './import';
import { LocalSubmitApi } from './submit';

const program = new commander.Command();

function _export() {}

function show() {}

async function ctxFromConfig(configFile?: string): Promise<ApiContext> {
    const config = loadConfig(configFile);
    console.log(config);
    const env = new ApiEnvironment(config);
    const context = new LocalApiContext(env);
    await env.sequelize.sync();

    return context;
}

// tslint:disable:no-unsafe-any

program
    .name('turingarena')
    .version('1.0')
    .option('-c, --config <path>', 'configuration file', 'turingarena.config.json');

program
    .command('serve')
    .description('start TuringArena server')
    .action(opts => {
        serve(loadConfig(opts.parent.config));
    });

program
    .command('import [dir]')
    .description('import a contest')
    .action(async (dir, opts) => {
        const ctx = await ctxFromConfig(opts.parent.config);
        await ctx.api(ContestImportApi).importContest(dir);
    });

program
    .command('submit <user> <contest> <problem> <solution>')
    .description('create a submission')
    .action(async (user, contest, problem, solution, opts) => {
        const ctx = await ctxFromConfig(opts.parent.config);
        await ctx.api(LocalSubmitApi).submitLocalFile(user, contest, problem, solution);
    });

program
    .command('export')
    .description('export a contest')
    .action(_export);

program
    .command('show')
    .description('show information about a contest')
    .action(show);

program.parseAsync(process.argv).catch(e => {
    process.emit('uncaughtException', e);
});
