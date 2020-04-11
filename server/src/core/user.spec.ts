import { gql } from 'apollo-server-core';
import { ApiEnvironment, RemoteApiContext } from '../main/api-context';

it('test user add and delete', async () => {
    const response = await new RemoteApiContext(new ApiEnvironment()).execute({
        document: gql`
            mutation UserSpec {
                init
                createUser(user: { name: "Alessandro Righi", username: "alerighi", token: "alerighi", role: ADMIN })
                updateUser(user: { name: "Alessandro Righi", username: "alerighi", token: "alerighi2", role: USER })
                deleteUser(user: "alerighi")
            }
        `,
    });

    expect(response.errors).toBeUndefined();
});
