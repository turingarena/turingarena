import * as DataLoader from 'dataloader';
import { BeforeCreate, Column, DataType, Model, PrimaryKey } from 'sequelize-typescript';
import { v4 as uuidv4 } from 'uuid';
import { ApiContext } from './api-context';

export abstract class BaseModel<T> extends Model<T> {
    createdAt!: Date;
    updatedAt!: Date;
}

export abstract class UuidBaseModel<T> extends BaseModel<T> {
    @PrimaryKey
    @Column(DataType.UUIDV4)
    id!: string;

    @BeforeCreate
    static generateUuid(entity: UuidBaseModel<unknown>) {
        entity.id = uuidv4();
    }
}

export function createByIdDataLoader<T extends UuidBaseModel<T>>(ctx: ApiContext, modelClass: new () => T) {
    return createSimpleLoader<string, T>(key => ctx.table(modelClass).findByPk(key));
}

export function createSimpleLoader<TKey, TValue>(
    loadByKey: (key: TKey) => Promise<TValue | null>,
    makeError: (key: TKey) => Error = key => new Error(`invalid key ${key}`),
) {
    return new DataLoader<TKey, TValue>(
        keys => Promise.all(keys.map(async key => (await loadByKey(key)) ?? makeError(key))),
        {
            cacheKeyFn: key => (JSON.stringify(key) as unknown) as TKey,
        },
    );
}
