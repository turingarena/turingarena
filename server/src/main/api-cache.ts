import { ApiContext } from './api-context';

export abstract class ApiCache {
    constructor(readonly ctx: ApiContext) {}
}
