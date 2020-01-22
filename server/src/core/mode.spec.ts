import * as fs from 'fs';
import { ModelRoot } from '../main/model-root';
import { Contest } from './contest';
import { Problem } from './problem';
import { Submission } from './submission';
import { SubmissionFile } from './submission-file';
import { User } from './user';

it('test submission files', async () => {
    const root = new ModelRoot();
    await root.sequelize.sync();

    const user = await root.table(User).create({
        username: 'alerighi',
        name: '',
        token: '',
        privilege: 0,
    });

    const problem = await root.table(Problem).create({
        name: 'problem',
        files: [],
    });

    const contest = await root.table(Contest).create({
        name: 'contest',
        title: '',
        start: Date.now(),
        end: Date.now(),
        users: [user],
        problems: [problem],
    });

    const submission = await root.table(Submission).create(
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
            include: [root.table(SubmissionFile)],
        },
    );

    console.log(submission);

    await submission.extract(await fs.promises.mkdtemp('tatest'));
});
