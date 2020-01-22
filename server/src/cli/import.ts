import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { Contest } from '../core/contest';
import { ContestProblemAssignment } from '../core/contest-problem-assignment';
import { importProblemFiles } from '../core/material/problem-task-info';
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

    const contest = await root.table(Contest).create(metadata);

    await contest.loadFiles(root, path.join(dir, 'files'));

    for (const user of metadata.users) {
        await contest.createParticipation(
            {
                user: {
                    ...user,
                    role: user.role === 'admin' ? UserRole.ADMIN : UserRole.USER,
                },
            },
            {
                include: [root.table(User)],
            },
        );
    }

    for (const name of metadata.problems) {
        const problem = await root.table(Problem).create({
            name,
        });

        await importProblemFiles(problem, path.join(dir, name));

        await root.table(ContestProblemAssignment).create({
            contestId: contest.id,
            problemId: problem.id,
        });

        console.log(await problem.getTaskInfo());
    }
}
