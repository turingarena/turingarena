import { readFileSync } from 'fs';
import { Dialect } from 'sequelize/types';

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

export function loadConfig(): Config {
    try {
        return JSON.parse(readFileSync(configFilePath).toString());
    } catch {
        return defaultConfig;
    }
}
