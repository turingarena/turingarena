import { Model } from 'sequelize-typescript';
import { ModelRootSequelize } from './model-root';

export abstract class BaseModel<T> extends Model<T> {
    modelRoot = (this.sequelize as ModelRootSequelize).modelRoot;
}
