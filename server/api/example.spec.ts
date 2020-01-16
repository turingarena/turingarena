import { gql } from 'apollo-server-core';
import { ApiContext } from '.';
import { InitMutation, InitMutationVariables } from '../generated/graphql-types';

it('should init', async () => {
    const response = await new ApiContext().execute<InitMutation, InitMutationVariables>({
        document: gql`
            mutation Init {
                init
            }
        `,
    });

    expect(response.data?.init).toBeDefined();
});
