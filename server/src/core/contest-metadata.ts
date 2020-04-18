export type UserRole = 'user' | 'admin';

export interface UserMetadata {
    username: string;
    token: string;
    name: string;
    role?: UserRole;
}

export interface ContestMetadata {
    name: string;
    title: string;
    start: string;
    end: string;
    users: UserMetadata[];
    problems: string[];
}
