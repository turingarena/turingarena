import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { Contest } from '../core/contest';
import { ContestProblemAssignment } from '../core/contest-problem-assignment';
import { FileCollectionApi } from '../core/file-collection';
import { ProblemTaskInfoApi } from '../core/material/problem-task-info';
import { Participation } from '../core/participation';
import { Problem } from '../core/problem';
import { User, UserRole } from '../core/user';
import { ApiObject } from '../main/api';

export interface ContestMetadata {
    name: string;
    title: string;
    start: string;
    end: string;
    users: Array<{
        username: string;
        token: string;
        name: string;
        role?: 'user' | 'admin';
    }>;
    problems: string[];
}

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

        const contestFileCollectionId = await this.ctx
            .api(FileCollectionApi)
            .createFileCollection(path.join(dir, 'files'));

        const contest = await this.ctx.table(Contest).create({
            fileCollectionId: contestFileCollectionId,
            ...metadata,
        });

        for (const userData of metadata.users) {
            const user = await this.ctx.table(User).create({
                ...userData,
                role: userData.role === 'admin' ? UserRole.ADMIN : UserRole.USER,
            });
            await this.ctx.table(Participation).create({ userId: user.id, contestId: contest.id });
        }

        for (const name of metadata.problems) {
            const fileCollectionId = await this.ctx.api(FileCollectionApi).createFileCollection(path.join(dir, name));

            const problem = await this.ctx.table(Problem).create({
                name,
                fileCollectionId,
            });

            await this.ctx.table(ContestProblemAssignment).create({
                contestId: contest.id,
                problemId: problem.id,
            });

            console.log(await this.ctx.api(ProblemTaskInfoApi).getProblemTaskInfo(problem));
        }
    }
}
