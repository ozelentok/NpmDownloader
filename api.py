import curio
import npm_api
import version_utils

async def wait_for_all_tasks(tasks):
    for task in tasks:
        await task.join()

async def download_package(name, download_dir):
    latest_version = await add_version_for(name)
    await npm_api.download_tar_ball_of(name, latest_version, download_dir)
    dependencies = await get_dependencies_with_versions(name, latest_version)
    tasks = []
    for package, version in dependencies.items():
        tasks.append(await curio.spawn(download_dependencies({package: version}, download_dir)))
    for t in tasks:
        await t.join()

async def download_dependencies(dependencies, download_dir):
    download_queue = curio.Queue()
    await download_queue.put(dependencies)
    while not download_queue.empty():
        packages = await download_queue.get()
        for package, version in packages.items():
            await download_dependency(package, version, download_dir)
            await download_queue.put(await get_dependencies_with_versions(package, version))
        await download_queue.task_done()

async def download_dependency(name, version, download_dir):
    await npm_api.download_tar_ball_of(name, version, download_dir)

async def add_version_for(name):
    return await npm_api.get_latest_version_of(name)

async def get_dependencies_with_versions(name, ver):
    dependencies = await npm_api.get_dependencies_of(name, ver)
    tasks = {}
    for package, version in dependencies.items():
        tasks[package] = await curio.spawn(get_latest_satisfying_version(package, version))
    dependencies_with_versions = {}
    for package, task in tasks.items():
        dependencies_with_versions[package] = await task.join()
    return dependencies_with_versions

async def get_latest_satisfying_version(name, version):
    versions = await npm_api.get_versions_of(name)
    return version_utils.get_lastest_satisfying_version(versions, version)
