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

export class PackageService extends Service {
    private readonly cache = new Map<string, string>();

    async getSourceBranches(packageId: string, locationName: string) {
        await this.ensureGit();

        const locationPart = locationName === 'default' ? '' : `/location/${locationName}`;

        const output = await exec2(
            `git
                --git-dir ${this.ctx.config.gitDir}
                for-each-ref
                --format="%(refname)"
                refs/heads${locationPart}/*
                refs/heads/${packageId}
                refs/heads/${packageId}${locationPart}
                refs/heads/${packageId}${locationPart}/*
                `.replace(/\n/g, ' '),
        );

        const refs = output.split('\n');
        refs.pop(); // Empty string after last EOL

        return refs.map(refName => refName.substring('refs/heads/'.length));
    }

    async checkout(branchName: string, path: string) {
        await this.ensureGit();

        const cached = await this.getCachedArchive(branchName, path);
        if (cached !== null) return cached;

        return this.checkoutUncached(branchName, path);
    }

    private async getCachedArchive(branchName: string, path: string) {
        const commitHashOutput = await exec2(`git --git-dir ${this.ctx.config.gitDir} rev-parse ${branchName}`);
        const [commitHash] = commitHashOutput.split('\n');
        const archiveHash = this.cache.get(this.checkoutCacheKey(commitHash, path));
        if (archiveHash === undefined) return null;

        return { commitHash, archiveHash };
    }

    private checkoutCacheKey(commitHash: string, path: string) {
        return `${commitHash}:${path}`;
    }

    private async checkoutUncached(branchName: string, path: string) {
        await exec2(`mkdir -p ${this.ctx.config.cachePath}/git-clones`);
        const cloneTempDir = await fs.mkdtemp(`${this.ctx.config.cachePath}/git-clones/`);

        await exec2(`mkdir -p ${this.ctx.config.cachePath}/archives-temp`);
        const archiveTempDir = await fs.mkdtemp(`${this.ctx.config.cachePath}/archives-temp/`);

        try {
            await exec2(`git clone --local --shared --branch ${branchName} ${this.ctx.config.gitDir} ${cloneTempDir}`);
            const commitHashOutput = await exec2(`git --git-dir ${cloneTempDir}/.git rev-parse HEAD`);
            const [commitHash] = commitHashOutput.split('\n');

            await exec2(`rm -r ${cloneTempDir}/.git`);

            try {
                await fs.access(`${cloneTempDir}/${path}`);
            } catch (error) {
                return { commitHash, archiveHash: null, error };
            }

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
                // Copy archive atomically
                await exec2(`mv --no-target-directory ${archiveTempDir} ${archivePath}`);
            } catch (error) {
                // Move failed, check that archive exists
                await fs.access(archivePath);
            }

            this.cache.set(this.checkoutCacheKey(commitHash, path), archiveHash);

            return { commitHash, archiveHash };
        } finally {
            await exec2(`rm -rf ${cloneTempDir}`);
            await exec2(`rm -rf ${archiveTempDir}`);
        }
    }

    private archivePath(hash: string) {
        return `${this.ctx.config.cachePath}/archives/${hash}`;
    }

    private async ensureGit() {
        await exec2(`git --git-dir ${this.ctx.config.gitDir} init --bare`);
    }

    run() {
        return noop;
    }
}
