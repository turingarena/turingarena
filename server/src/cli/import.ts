import * as fs from 'fs';
import * as mime from 'mime-types';
import * as path from 'path';
import * as yaml from 'yaml';
import { ApiContext } from '../api/index';
import { UserPrivilege } from '../model/user';

/**
 * Walk the directory and inserts all the files in the database
 *
 * @param fileList a list of File
 * @param base directory to walk
 * @param ctx API context
 */
async function addFiles(ctx, fileList, base: string, dir: string = '') {
    const files = fs.readdirSync(path.join(base, dir));
    for (const file of files) {
        const relPath = path.join(dir, file);
        if (fs.statSync(path.join(base, relPath)).isDirectory()) {
            await addFiles(ctx, fileList, base, relPath);
        } else {
            const content = fs.readFileSync(path.join(base, relPath));
            const type = mime.lookup(file);
            await fileList.addProblemFile(
                await ctx.db.ProblemFile.create(
                    {
                        path: relPath,
                        file: {
                            type: type !== false ? type : 'unknown',
                            content,
                        },
                    },
                    { include: [ctx.db.File] },
                ),
            );
        }
    }
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
    const metadata = yaml.parse(turingarenaYAML);

    const contest = await ctx.db.Contest.create(metadata);

    //await addFiles(ctx, contest, path.join(dir, 'files'));

    for (const user of metadata.users) {
        await contest.createUser({
            ...user,
            privilege:
                user.role === 'admin'
                    ? UserPrivilege.ADMIN
                    : UserPrivilege.USER,
        });
    }

    for (const name of metadata.problems) {
        const problem = await ctx.db.Problem.create({
            name,
        });

        await addFiles(ctx, problem, path.join(dir, name));
        await contest.addProblem(problem);

        await problem.extract(ctx, '/tmp/prob1');
    }
}
