import { gql } from 'apollo-server-core';
import { ApiContext } from '.';
import { InitMutation, InitMutationVariables } from '../generated/graphql-types';

it('test user add and delete', async () => {
    const response = await new ApiContext().execute<InitMutation, InitMutationVariables>({
        document: gql`
        mutation UserAddAndDelete {
            init {
                __typename
            }
            createUser(user: {
                name: "Alessandro Righi",
                username: "alerighi",
                token: "alerighi",
                isAdmin: true,
            }) {
                user("alrighi") {
                    name
                }
            }
            updateUser(user: {
                name: "Alessandro Righi",
                username: "alerighi",
                token: "alerighi2",
                isAdmin: false,
            }) {
                user("alerighi") {
                    isAdmin
                }
            }
            removeUser(user: "alerighi")
        }`,
    });

    expect(response.data?.init).toEqual({
        init: {
            __typename: "Query"
        },
        createUser: {
            user: {
                name: "Alessandro Righi"
            }
        },
        updateUser: {
            user: {
                isAdmin: false
            }
        },
        removeUser: {
            __typename: "Query"
        },
    });
});
