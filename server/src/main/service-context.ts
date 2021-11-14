import { Auth } from '../core/auth';
import { unreachable } from '../util/unreachable';
import { InstanceContext } from './instance-context';
import { Service } from './service';

/** Long-lived context for services. */
export class ServiceContext {
    services = new Map<unknown, Service>();

    constructor(
        readonly instanceContext: InstanceContext,
        readonly serviceClasses: Array<new (ctx: ServiceContext) => Service>,
    ) {
        for (const serviceClass of serviceClasses) {
            const service = new serviceClass(this);
            this.services.set(serviceClass, service);
        }
    }

    runAll() {
        const cleanups: Array<() => void> = [];
        for (const service of this.services.values()) {
            cleanups.push(service.run());
        }

        return () => {
            for (const cleanup of cleanups) cleanup();
        };
    }

    config = this.instanceContext.config;
    db = this.instanceContext.db;
    table = this.instanceContext.table;

    // TODO: load secret from environment
    readonly auth = new Auth(this);

    service = <T extends Service>(serviceClass: new (ctx: ServiceContext) => T): T =>
        (this.services.get(serviceClass) as T) ?? unreachable(`service not available`);
}
