import { ObjectiveDefinition } from './objective-definition';

export interface TestCaseData {
    objective: ObjectiveDefinition;
    objectiveIndex: number;
    testCaseIndex: number;
    timeUsage: number | null;
    memoryUsage: number | null;
    message: string | null;
    score: number | null;
}
