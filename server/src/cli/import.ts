import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { getProblemMetadata, importProblemFiles } from '../core/problem-util';
import { UserRole } from '../core/user';
import { ApiContext } from '../main/context';

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
 * @param ctx the API context
 * @param dir base directoyr of the contest
 */
export async function importContest(ctx: ApiContext, dir = process.cwd()) {
    const turingarenaYAMLPath = path.join(dir, 'turingarena.yaml');

    if (!fs.existsSync(turingarenaYAMLPath))
        throw Error('Invalid contest directory');

    const turingarenaYAML = fs.readFileSync(turingarenaYAMLPath).toString();
    const metadata = yaml.parse(turingarenaYAML) as ContestMetadata;

    const contest = await ctx.db.Contest.create(metadata);

    await contest.loadFiles(ctx, path.join(dir, 'files'));

    for (const user of metadata.users)
        await contest.createParticipation(
            {
                user: {
                    ...user,
                    role:
                        user.role === 'admin' ? UserRole.ADMIN : UserRole.USER,
                },
            },
            {
                include: [ctx.db.User],
            },
        );

    for (const name of metadata.problems) {
        const problem = await ctx.db.Problem.create({
            name,
        });

        await importProblemFiles(ctx, problem, path.join(dir, name));

        await ctx.db.ContestProblem.create({
            contestId: contest.id,
            problemId: problem.id,
        });

        console.log(await getProblemMetadata(ctx, problem));
    }
}
