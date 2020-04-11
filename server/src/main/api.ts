import { ApiContext } from './api-context';

export abstract class ApiObject {
    constructor(readonly ctx: ApiContext) {}
}
