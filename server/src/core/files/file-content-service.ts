import { Service } from '../../main/service';
import { unreachable } from '../../util/unreachable';
import { FileContent } from './file-content';

export class FileContentService extends Service {
    // FIXME: caching file content in RAM, not very smart
    readonly cache = new Map<string, FileContent>();

    getContent(id: string) {
        return this.cache.get(id) ?? unreachable(`file content not found`);
    }

    publish(fileContent: FileContent) {
        // TODO: allow exposing a file only to some users
        this.cache.set(fileContent.id, fileContent);
    }
}
