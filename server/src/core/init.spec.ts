import { gql } from 'apollo-server-core';
import { RemoteApiContext } from '../main/api-context';
import { InstanceContext } from '../main/instance-context';
import { ServiceContext } from '../main/service-context';

it('test user add and delete', async () => {
    const response = await new RemoteApiContext(new ServiceContext(new InstanceContext(), [])).execute({
        document: gql`
            mutation InitSpec {
                init
            }
        `,
    });

    expect(response.errors).toBeUndefined();
});
