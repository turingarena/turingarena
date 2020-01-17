import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';
import { ApiContext } from '../api/index';
import { UserPrivilege } from '../model/user';


export async function _import(dir = process.cwd()) {
    const ctx = new ApiContext();

    await ctx.sequelize.sync();

    const turingarenaYAMLPath = path.join(dir, 'turingarena.yaml');

    if (!fs.existsSync(turingarenaYAMLPath))
        throw 'Invalid contest directory';

    const turingarenaYAML = fs.readFileSync(turingarenaYAMLPath).toString();
    const contest = yaml.parse(turingarenaYAML);

    console.info('Importing contest', contest);

    for (const user of contest.users) {
        console.debug('Import user', user);
        ctx.db.User.create({
            username: user.username,
            name: user.name,
            token: user.token,
            privilege: user.role == 'admin' ? UserPrivilege.ADMIN : UserPrivilege.USER,
        });
    }

    for (const problem of contest.problems) {
        console.debug('Import problem', problem);


        ctx.db.Problem.create({
            name: problem,
            files: [],
        })
    }
}
