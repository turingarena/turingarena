import * as fs from 'fs';
import * as path from 'path';
import { Contest, ContestData } from '../core/contest';
import { createArchive } from '../core/files/archive';
import { ApiContext } from '../main/api-context';

/**
 * Import a contest in the database
 *
 * @param dir base directory of the contest
 */
export async function importContest(ctx: ApiContext, dir = process.cwd()) {
    if (!fs.existsSync(path.join(dir, 'turingarena.yaml'))) throw Error('Invalid contest directory');
    if (fs.existsSync('db.sqlite3')) {
        fs.copyFileSync('db.sqlite3', 'db.sqlite3.bak');
    }
    const contestArchiveId = await createArchive(ctx, dir);
    const contest = await ctx.table(ContestData).create({
        archiveId: contestArchiveId,
    });

    console.log(await new Contest(contest.id, ctx).getMetadata());
}
