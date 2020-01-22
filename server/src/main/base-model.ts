import { Model } from 'sequelize-typescript';
import { SequelizeWithContext } from './context';

export abstract class BaseModel<T> extends Model<T> {
    context? = (this.sequelize as SequelizeWithContext).context;
}
