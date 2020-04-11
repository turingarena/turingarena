import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { Contest } from '../core/contest';
import { ContestProblemAssignment } from '../core/contest-problem-assignment';
import { createFileCollection } from '../core/file-collection';
import { Participation } from '../core/participation';
import { Problem } from '../core/problem';
import { User, UserRole } from '../core/user';
import { ModelRoot } from '../main/model-root';

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

/**
 * Import a contest in the database
 *
 * @param root the model root
 * @param dir base directory of the contest
 */
export async function importContest(root: ModelRoot, dir = process.cwd()) {
    const turingarenaYAMLPath = path.join(dir, 'turingarena.yaml');

    if (!fs.existsSync(turingarenaYAMLPath)) throw Error('Invalid contest directory');

    const turingarenaYAML = fs.readFileSync(turingarenaYAMLPath).toString();
    const metadata = yaml.parse(turingarenaYAML) as ContestMetadata;

    const contestFileCollectionId = await createFileCollection(root, path.join(dir, 'files'));

    const contest = await root.table(Contest).create({
        fileCollectionId: contestFileCollectionId,
        ...metadata,
    });

    for (const userData of metadata.users) {
        const user = await root.table(User).create({
            ...userData,
            role: userData.role === 'admin' ? UserRole.ADMIN : UserRole.USER,
        });
        await root.table(Participation).create({ userId: user.id, contestId: contest.id });
    }

    for (const name of metadata.problems) {
        const fileCollectionId = await createFileCollection(root, path.join(dir, name));

        const problem = await root.table(Problem).create({
            name,
            fileCollectionId,
        });

        await root.table(ContestProblemAssignment).create({
            contestId: contest.id,
            problemId: problem.id,
        });

        console.log(await problem.getTaskInfo());
    }
}
