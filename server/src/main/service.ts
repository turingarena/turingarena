import { ServiceContext } from './service-context';

export abstract class Service {
    constructor(readonly ctx: ServiceContext) {}

    run(): () => void {
        return () => {
            // No-op
        };
    }
}
