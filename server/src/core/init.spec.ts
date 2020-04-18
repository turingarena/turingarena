import { gql } from 'apollo-server-core';
import { ApiEnvironment, RemoteApiContext } from '../main/api-context';

it('test user add and delete', async () => {
    const response = await new RemoteApiContext(new ApiEnvironment()).execute({
        document: gql`
            mutation InitSpec {
                init
            }
        `,
    });

    expect(response.errors).toBeUndefined();
});
