export interface UserMetadata {
    username: string;
    token: string;
    name: string;
}

export interface ContestMetadata {
    title: string;
    start: string;
    end?: string;
    users: UserMetadata[];
    problems: string[];
}
