import { promises as fs } from 'fs';
import { defaultConfig } from '../../main/config';
import { InstanceContext } from '../../main/instance-context';
import { ServiceContext } from '../../main/service-context';
import { exec2, PackageService } from './package-service';

it('copies files and computes a stable hash', async () => {
    await testCheckout(
        async tempDir => {
            await exec2(`echo "test" > ${tempDir}/git-input/test.txt`);
            await exec2(`git -C ${tempDir}/git-input add test.txt`);
            await exec2(`git -C ${tempDir}/git-input commit -m "Initial"`);
        },
        '.',
        async (tempDir, hash) => {
            expect(hash).toBe('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');

            await expect(exec2(`ls ${tempDir}/cache/archives/${hash}/.git`)).rejects.toThrow();
            await exec2(`ls ${tempDir}/cache/archives/${hash}/test.txt`);
        },
    );
});

it('resolves safe and unsafe symlinks correctly', async () => {
    await testCheckout(
        async tempDir => {
            await exec2(`mkdir ${tempDir}/git-input/dependency/`);
            await exec2(`echo "dependency" > ${tempDir}/git-input/dependency/dependency.txt`);
            await exec2(`mkdir ${tempDir}/git-input/archive/`);
            await exec2(`ln -s ../dependency ${tempDir}/git-input/archive/dependency`);
            await exec2(`echo "linked" > ${tempDir}/git-input/archive/linked.txt`);
            await exec2(`ln -s ./linked.txt ${tempDir}/git-input/archive/link.txt`);
            await exec2(`git -C ${tempDir}/git-input add .`);
            await exec2(`git -C ${tempDir}/git-input commit -m "Initial"`);
        },
        'archive',
        async (tempDir, hash) => {
            expect(typeof hash).toBe('string');

            await exec2(`ls ${tempDir}/cache/archives/${hash}/dependency/dependency.txt`);
            await exec2(`ls ${tempDir}/cache/archives/${hash}/linked.txt`);
            await exec2(`readlink ${tempDir}/cache/archives/${hash}/link.txt`);
        },
    );
});

it('returns null if directory is not found', async () => {
    await testCheckout(
        async tempDir => {
            await exec2(`echo "test" > ${tempDir}/git-input/test.txt`);
            await exec2(`git -C ${tempDir}/git-input add test.txt`);
            await exec2(`git -C ${tempDir}/git-input commit -m "Initial"`);
        },
        'non-existent',
        async (tempDir, hash) => {
            expect(hash).toBeNull();
        },
    );
});

it('fails on unsafe symlinks without referent', async () => {
    await expect(
        testCheckout(
            async tempDir => {
                await exec2(`ln -s ../non-existent ${tempDir}/git-input/bad-link`);
                await exec2(`git -C ${tempDir}/git-input add .`);
                await exec2(`git -C ${tempDir}/git-input commit -m "Initial"`);
            },
            '.',
            () => Promise.resolve(),
        ),
    ).rejects.toThrow();
});

async function withTempDir(inner: (tempDir: string) => Promise<void>) {
    const tempDir = await fs.mkdtemp('/tmp/turingarena-test-');

    try {
        await inner(tempDir);
    } finally {
        // await exec2(`rm -rf ${tempDir}`);
    }
}

async function testCheckout(
    prepareCommit: (tempDir: string) => Promise<void>,
    path: string,
    checkArchive: (tempDir: string, hash: string | null) => Promise<void>,
) {
    await withTempDir(async tempDir => {
        await exec2(`mkdir ${tempDir}/git`);
        await exec2(`mkdir ${tempDir}/git-input`);
        await exec2(`git --git-dir ${tempDir}/git init --bare`);
        await exec2(`git init ${tempDir}/git-input`);

        await prepareCommit(tempDir);

        await exec2(`git --git-dir ${tempDir}/git-input/.git push ${tempDir}/git HEAD:test`);

        const serviceContext = new ServiceContext(
            new InstanceContext({
                ...defaultConfig,
                cachePath: `${tempDir}/cache`,
                gitDir: `${tempDir}/git`,
            }),
            [PackageService],
        );

        const { archiveHash } = await serviceContext.service(PackageService).checkout('test', path);
        await checkArchive(tempDir, archiveHash ?? null);
    });
}
