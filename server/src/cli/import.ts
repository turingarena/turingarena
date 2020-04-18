import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { Contest } from '../core/contest';
import { ContestMetadata } from '../core/contest-metadata';
import { ArchiveApi } from '../core/files/archive';
import { Participation } from '../core/participation';
import { User, UserRole } from '../core/user';
import { ApiObject } from '../main/api';

export class ContestImportApi extends ApiObject {
    /**
     * Import a contest in the database
     *
     * @param dir base directory of the contest
     */
    async importContest(dir = process.cwd()) {
        const turingarenaYAMLPath = path.join(dir, 'turingarena.yaml');

        if (!fs.existsSync(turingarenaYAMLPath)) throw Error('Invalid contest directory');

        const turingarenaYAML = fs.readFileSync(turingarenaYAMLPath).toString();

        const metadata = yaml.parse(turingarenaYAML) as ContestMetadata;
        const contestArchiveId = await this.ctx.api(ArchiveApi).createArchive(dir);

        const contest = await this.ctx.table(Contest).create({
            archiveId: contestArchiveId,
            ...metadata,
        });

        for (const userData of metadata.users) {
            const user = await this.ctx.table(User).create({
                ...userData,
                role: userData.role === 'admin' ? UserRole.ADMIN : UserRole.USER,
            });
            await this.ctx.table(Participation).create({ userId: user.id, contestId: contest.id });
        }

        // TODO
        // for (const name of metadata.problems) {
        //     const archiveId = await this.ctx.api(ArchiveApi).createArchive(path.join(dir, name));

        //     const problem = await this.ctx.table(Problem).create({
        //         name,
        //         archiveId,
        //     });

        //     await this.ctx.table(ContestProblemAssignment).create({
        //         contestId: contest.id,
        //         problemId: problem.id,
        //     });

        //     console.log(await this.ctx.api(ProblemTaskInfoApi).getProblemTaskInfo(problem));
        // }
    }
}
