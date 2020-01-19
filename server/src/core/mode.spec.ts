import * as fs from 'fs';
import { ApiContext } from '../main/context';
import { Contest } from './contest';
import { Problem } from './problem';
import { Submission } from './submission';
import { SubmissionFile } from './submission-file';
import { User } from './user';

it('test submission files', async () => {
    const ctx = new ApiContext();
    await ctx.sequelize.sync();

    const user = await ctx.table(User).create({
        username: 'alerighi',
        name: '',
        token: '',
        privilege: 0,
    });

    const problem = await ctx.table(Problem).create({
        name: 'problem',
        files: [],
    });

    const contest = await ctx.table(Contest).create({
        name: 'contest',
        title: '',
        start: Date.now(),
        end: Date.now(),
        users: [user],
        problems: [problem],
    });

    const submission = await ctx.table(Submission).create(
        {
            user,
            contest,
            problem,
            submissionFiles: [
                {
                    fieldId: 'solution',
                    file: {
                        content: Buffer.from('ciao ciao'),
                        type: 'text/plain',
                        // path: 'solution::solution.cpp',
                    },
                },
            ],
        },
        {
            include: [ctx.table(SubmissionFile)],
        },
    );

    console.log(submission);

    await submission.extract(await fs.promises.mkdtemp('tatest'));
});
