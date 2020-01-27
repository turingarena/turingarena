import { Model } from 'sequelize-typescript';
import { ModelRootSequelize } from './model-root';

export abstract class BaseModel<T> extends Model<T> {
    root = (this.sequelize as ModelRootSequelize).root;
}
