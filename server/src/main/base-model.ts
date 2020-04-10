import { BeforeCreate, Column, DataType, Model, PrimaryKey } from 'sequelize-typescript';
import { v4 as uuidv4 } from 'uuid';
import { ModelRootSequelize } from './model-root';

export abstract class BaseModel<T> extends Model<T> {
    root = (this.sequelize as ModelRootSequelize).root;
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
