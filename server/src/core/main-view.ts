import { gql } from 'apollo-server-core';
import { ModelRoot } from '../main/model-root';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestView } from './contest-view';
import { User } from './user';

export const mainViewSchema = gql`
    type MainView {
        user: User
        title: Text!
        contestView: ContestView
    }
`;

export class MainView {
    constructor(readonly root: ModelRoot, readonly user: User | null) {
        console.log({ root, arguments });
    }

    async getContest() {
        return this.root.table(Contest).findOne({ where: { name: 'default' } });
    }
}

export const mainViewResolvers: ResolversWithModels<{
    MainView: MainView;
}> = {
    MainView: {
        user: ({ user }) => user,
        title: async mainView => {
            const contest = await mainView.getContest();

            return [{ value: contest?.title ?? 'TuringArena' }];
        },
        contestView: async mainView => {
            const contest = await mainView.getContest();
            if (contest === null) return null;

            return new ContestView(contest, mainView.user);
        },
    },
};
