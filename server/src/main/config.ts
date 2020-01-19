import { readFileSync } from 'fs';
import * as path from 'path';
import { Options } from 'sequelize';

export interface Config {
    db: Options;
    port: number;
    host: string;
    taskMakerExecutable: string;
    cachePath: string;
}

export const defaultConfig: Config = {
    db: {
        storage: ':memory:',
        dialect: 'sqlite',
    },
    port: 3000,
    host: 'localhost',
    taskMakerExecutable: 'task-maker-rust',
    cachePath: path.join(process.env.HOME ?? '/tmp', '.cache/turingarena/'),
};

export function loadConfig(configPath?: string): Config {
    if (configPath === undefined) return defaultConfig;

    const config = JSON.parse(readFileSync(configPath).toString()) as Config;

    // FIXME: is there a better way?
    return {
        db: config.db ?? defaultConfig.db,
        port: config.port ?? defaultConfig.port,
        host: config.host ?? defaultConfig.host,
        taskMakerExecutable: config.taskMakerExecutable ?? defaultConfig.taskMakerExecutable,
        cachePath: config.cachePath ?? defaultConfig.cachePath,
    };
}
