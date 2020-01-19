import { readFileSync } from 'fs';
import { Options } from 'sequelize';

export interface Config {
    db: Options;
    port: number;
    host: string;
}

export const defaultConfig: Config = {
    db: {
        storage: ':memory:',
        dialect: 'sqlite',
    },
    port: 3000,
    host: 'localhost',
};

export function loadConfig(path?: string): Config {
    if (path === undefined) return defaultConfig;

    return JSON.parse(readFileSync(path).toString());
}
