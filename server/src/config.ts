import { readFileSync } from 'fs';
import { Dialect } from 'sequelize';

export interface Config {
    dbPath: string;
    dbDialect: Dialect;
    port: number;
    host: string;
}

const configFilePath = 'turingarena.config.json';

const defaultConfig: Config = {
    dbPath: ':memory:',
    dbDialect: 'sqlite',
    port: 3000,
    host: 'localhost',
};

export function loadConfig(path?: string): Config {
    if (path === undefined) {
        return defaultConfig;
    }
    try {
        return JSON.parse(readFileSync(path ?? configFilePath).toString());
    } catch {
        console.warn('Cannot read config file: using defualt config');

        return defaultConfig;
    }
}
