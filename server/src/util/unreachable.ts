export function unreachable(reason?: string): never {
    throw new Error(reason);
}
