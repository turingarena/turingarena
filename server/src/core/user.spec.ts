import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/context';

it('test user add and delete', async () => {
    const response = await new ApiContext().execute({
        document: gql`
            mutation UserSpec {
                init
                createUser(
                    user: {
                        name: "Alessandro Righi"
                        username: "alerighi"
                        token: "alerighi"
                        role: ADMIN
                    }
                )
                updateUser(
                    user: {
                        name: "Alessandro Righi"
                        username: "alerighi"
                        token: "alerighi2"
                        role: USER
                    }
                )
                deleteUser(user: "alerighi")
            }
        `,
    });

    expect(response.errors).toBeUndefined();
});
