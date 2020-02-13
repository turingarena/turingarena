import { readFileSync } from 'fs';
import * as path from 'path';
import { Options } from 'sequelize';
import { randomBytes } from 'crypto';

export interface Config {
    db: Options;
    port: number;
    host: string;
    taskMakerExecutable: string;
    cachePath: string;
    skipAuth: boolean;
    secret: string;
}

export const defaultConfig: Config = {
    db: {
        storage: ':memory:',
        dialect: 'sqlite',
    },
    port: 3000,
    host: 'localhost',
    taskMakerExecutable: 'task-maker-rust',
    skipAuth: false,
    secret: randomBytes(48).toString('hex'),
    cachePath: path.join(process.env.HOME ?? '/tmp', '.cache/turingarena/'),
};

export function loadConfig(configPath?: string): Config {
    if (configPath === undefined) return defaultConfig;

    const config = JSON.parse(readFileSync(configPath).toString()) as Config;

    return { ...defaultConfig, ...config };
}
