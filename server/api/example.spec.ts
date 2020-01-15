import { gql } from 'apollo-server-core';
import { execute } from 'graphql';
import { executableSchema } from '.';
import { InitMutation } from '../generated/graphql-types';

it('should init', async () => {
    const response = await execute<InitMutation>(
        executableSchema,
        gql`
            mutation Init {
                init {
                    __typename
                }
            }
        `,
    );

    expect(response.data?.init).toBeDefined();
});
