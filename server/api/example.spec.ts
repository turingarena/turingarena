import { gql } from 'apollo-server-core';
import { localClient } from '../helpers/local';

it('should init', async () => {
    const response = await localClient.mutate({
        mutation: gql`
            mutation {
                init
            }
        `,
    });
    expect(response.data.init).toBeDefined();
});
