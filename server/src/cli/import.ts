import * as fs from 'fs';
import * as path from 'path';
import { Contest, ContestData } from '../core/contest';
import { ArchiveApi } from '../core/files/archive';
import { ApiObject } from '../main/api';

export class ContestImportApi extends ApiObject {
    /**
     * Import a contest in the database
     *
     * @param dir base directory of the contest
     */
    async importContest(dir = process.cwd()) {
        if (!fs.existsSync(path.join(dir, 'turingarena.yaml'))) throw Error('Invalid contest directory');

        const contestArchiveId = await this.ctx.api(ArchiveApi).createArchive(dir);
        const contest = await this.ctx.table(ContestData).create({
            archiveId: contestArchiveId,
        });

        console.log(await new Contest(contest.id, this.ctx).getMetadata(this.ctx));
    }
}
