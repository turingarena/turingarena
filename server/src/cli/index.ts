#!/usr/bin/env node

import * as commander from 'commander';
import { ApiContext, LocalApiContext } from '../main/api-context';
import { loadConfig } from '../main/config';
import { InstanceContext } from '../main/instance-context';
import { serve } from '../main/server';
import { ServiceContext } from '../main/service-context';
import { restoreContest } from './restore';
import { submitLocalFile } from './submit';

const program = new commander.Command();

function _export() {}

function show() {}

async function ctxFromConfig(configFile?: string): Promise<ApiContext> {
    const config = loadConfig(configFile);
    console.log(config);
    const instanceContext = new InstanceContext(config);
    const serviceContext = new ServiceContext(instanceContext, []);
    const context = new LocalApiContext(serviceContext);
    await instanceContext.db.sync();

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
    .option('--admin')
    .action(opts => {
        serve(loadConfig(opts.parent.config), opts.admin);
    });

program
    .command('submit <user> <contest> <problem> <solution>')
    .description('create a submission')
    .action(async (user, contest, problem, solution, opts) => {
        const ctx = await ctxFromConfig(opts.parent.config);
        await submitLocalFile(ctx, user, contest, problem, solution);
    });

program
    .command('init')
    .description('initialize database')
    .action(async opts => {
        const ctx = await ctxFromConfig(opts.parent.config);
        await ctx.db.sync();
    });

program
    .command('restore')
    .description('restore a contest')
    .action(restoreContest);

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
