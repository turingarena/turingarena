import { exec } from 'child_process';
import { promises as fs } from 'fs';
import { noop } from 'rxjs';
import { Service } from '../../main/service';

export async function exec2(line: string) {
    return new Promise<string>((resolve, reject) => {
        exec(line, (error, stdout) => {
            if (error === null) {
                resolve(stdout);
            } else {
                reject(error);
            }
        });
    });
}

export class ArchiveService extends Service {
    private readonly cache = new Map<string, string>();

    async checkout(branchName: string, path: string) {
        await exec2(`git --git-dir ${this.ctx.config.gitDir} init --bare`);

        const cachedHash = await this.getCachedArchive(branchName, path);
        if (cachedHash !== null) return cachedHash;

        return this.checkoutUncached(branchName, path);
    }

    private async getCachedArchive(branchName: string, path: string) {
        const commitId = await exec2(`git --git-dir ${this.ctx.config.gitDir} rev-parse ${branchName}`);
        const archivePath = this.cache.get(this.checkoutCacheKey(commitId, path));
        if (archivePath === undefined) return null;

        return archivePath;
    }

    private checkoutCacheKey(commitId: string, path: string) {
        return `${commitId}:${path}`;
    }

    private async checkoutUncached(branchName: string, path: string) {
        await exec2(`mkdir -p ${this.ctx.config.cachePath}/git-clones`);
        const cloneTempDir = await fs.mkdtemp(`${this.ctx.config.cachePath}/git-clones/`);

        await exec2(`mkdir -p ${this.ctx.config.cachePath}/archives-temp`);
        const archiveTempDir = await fs.mkdtemp(`${this.ctx.config.cachePath}/archives-temp/`);

        try {
            await exec2(`git clone --local --shared --branch ${branchName} ${this.ctx.config.gitDir} ${cloneTempDir}`);
            const commitId = await exec2(`git --git-dir ${cloneTempDir}/.git rev-parse HEAD`);
            await exec2(`rm -r ${cloneTempDir}/.git`);
            await exec2(
                `
                    cd ${cloneTempDir}/${path}
                    && rsync
                        --recursive
                        --links
                        --copy-unsafe-links
                        .
                        ${archiveTempDir}`.replace(/\n/g, ' '),
            );

            // See: https://reproducible-builds.org/docs/archives/
            const hashOutput = await exec2(
                `tar
                    --sort=name
                    --mtime=0
                    --owner=0
                    --group=0
                    --numeric-owner
                    --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime
                    --directory=${archiveTempDir}
                    --create
                | sha256sum`.replace(/\n/g, ' '),
            );
            const [archiveHash] = hashOutput.split(' ', 2);

            await exec2(`mkdir -p ${this.ctx.config.cachePath}/archives`);

            const archivePath = this.archivePath(archiveHash);
            try {
                // Archive exists, nothing to do
                await fs.access(archivePath);
            } catch (error) {
                // Copy archive atomically
                await exec2(`mv --no-target-directory ${archiveTempDir} ${archivePath}`);
            }

            this.cache.set(this.checkoutCacheKey(commitId, path), archiveHash);

            return archiveHash;
        } finally {
            await exec2(`rm -rf ${cloneTempDir}`);
            await exec2(`rm -rf ${archiveTempDir}`);
        }
    }

    private archivePath(hash: string) {
        return `${this.ctx.config.cachePath}/archives/${hash}`;
    }

    run() {
        return noop;
    }
}
