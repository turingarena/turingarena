// tslint:disable: no-implicit-dependencies
import { InMemoryCache } from 'apollo-cache-inmemory';
import ApolloClient from 'apollo-client';
import { ApolloLink, FetchResult, Observable, Operation } from 'apollo-link';
import { execute, GraphQLSchema } from 'graphql';
import { executableSchema } from '../api';

class LocalLink extends ApolloLink {
    constructor(private readonly schema: GraphQLSchema) { super(); }

    request(operation: Operation) {
        const {
            query,
            ...rest
        } = operation;

        const run = async () => execute({
            schema: this.schema,
            document: query,
            ...operation,
        });

        return new Observable<FetchResult>((observer) => {
            run().then(
                (response) => { observer.next(response); observer.complete(); },
                (error) => { observer.error(error); });
        });
    }
}

export const localClient = new ApolloClient({
    link: new LocalLink(executableSchema),
    cache: new InMemoryCache(),
});
