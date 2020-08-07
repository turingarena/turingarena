import { randomBytes } from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import { Options } from 'sequelize';

export interface Config {
    db: Options;
    port: number;
    host: string;
    taskMaker: {
        executable?: string;
        cachePath?: string;
        storeDir?: string;
        remote?: string;
    };
    cachePath: string;
    skipAuth: boolean;
    secret: string;
    webRoot: string;
}

const webPaths = [
    '/usr/local/share/turingarena/webnode',
    '/usr/share/turingarena/web',
    `${process.env.HOME}/.local/share/turingarena/web`,
];

const configPaths = [
    '/usr/local/etc/turingarena.conf.json',
    '/etc/turingarena.conf.json',
    `${process.env.HOME}/.config/turingarena/turingarena.conf.json`,
    `${process.cwd()}/.turingarena.conf.json`,
];

function firstPath(paths: string[]) {
    for (const p of paths) {
        if (fs.existsSync(p)) {
            return p;
        }
    }

    return null;
}

function findWebRoot() {
    try {
        return path.join(require.resolve('turingarena-web'), '..', 'build');
    } catch (e) {}

    let dir = firstPath(webPaths);

    if (dir !== null) {
        return dir;
    }

    dir = process.cwd();

    while (!fs.existsSync(path.join(dir, 'web')) && dir !== '/') {
        dir = path.resolve(dir, '../');
    }

    return path.join(dir, 'web/build');
}

export const defaultConfig: Config = {
    db: {
        storage: ':memory:',
        dialect: 'sqlite',
    },
    port: 3000,
    host: 'localhost',
    taskMaker: {
        executable: 'task-maker-rust',
    },
    skipAuth: false,
    secret: randomBytes(48).toString('hex'),
    cachePath: path.join(process.env.HOME ?? '/tmp', '.cache/turingarena/'),
    webRoot: findWebRoot(),
};

export function loadConfig(configPath?: string): Config {
    const configFile = configPath ?? firstPath(configPaths);

    if (configFile === null) {
        return defaultConfig;
    }

    const config = JSON.parse(fs.readFileSync(configFile).toString()) as Config;

    return { ...defaultConfig, ...config };
}
