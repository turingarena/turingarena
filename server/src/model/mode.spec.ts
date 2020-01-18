import * as fs from 'fs';
import { ApiContext } from '../api';

it('test submission files', async () => {
    const ctx = new ApiContext();
    await ctx.sequelize.sync();

    const user = await ctx.db.User.create({
        username: 'alerighi',
        name: '',
        token: '',
        privilege: 0,
    });

    const problem = await ctx.db.Problem.create({
        name: 'problem',
        files: [],
    });

    const contest = await ctx.db.Contest.create({
        name: 'contest',
        title: '',
        start: Date.now(),
        end: Date.now(),
        users: [user],
        problems: [problem],
    });

    const submission = await ctx.db.Submission.create(
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
            include: [ctx.db.SubmissionFile],
        },
    );

    console.log(submission);

    await submission.extract(await fs.promises.mkdtemp('tatest'));

});
