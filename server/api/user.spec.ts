import { gql } from 'apollo-server-core';
import { ApiContext } from '.';

it('test user add and delete', async () => {
    const response = await new ApiContext().execute({
        document: gql`
        mutation {
            init
            createUser(user: {
                name: "Alessandro Righi",
                username: "alerighi",
                token: "alerighi",
                isAdmin: true,
            })
            updateUser(user: {
                name: "Alessandro Righi",
                username: "alerighi",
                token: "alerighi2",
                isAdmin: false,
            })
            deleteUser(user: "alerighi")
        }`,
    });

    console.log(response);
    expect(response.data).toEqual({
        init: true,
        createUser: true,
        updateUser: true,
        removeUser: true,
    });
});
