import codecs
import json
import re
import io
import tarfile
import aiofiles

class NpmPackage:

    PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')

    __slots__ = ('name', 'version', 'file_path')

    def __init__(self, name: str, version: str, file_path: str):
        self.name = name
        self.version = version
        self.file_path = file_path

    async def get_dependencies(self) -> dict:
        package_info = await self.get_package_json()
        dependencies = {}
        if 'dependencies' in package_info:
            dependencies.update(package_info['dependencies'])
        if 'peerDependencies' in package_info:
            dependencies.update(package_info['peerDependencies'])
        return dependencies

    async def get_package_json(self) -> dict:
        async with aiofiles.open(self.file_path, "rb") as tar_file:
            tar_mem_stream = io.BytesIO(await tar_file.read())
        with tarfile.open(fileobj=tar_mem_stream, mode='r:gz') as tar_file:
            for internal_path in tar_file.getnames():
                if not NpmPackage.PACKAGE_JSON_PATH_PATTERN.match(internal_path):
                    continue
                member = tar_file.getmember(internal_path)
                with tar_file.extractfile(member) as file_stream:
                    return NpmPackage.parse_package_json(file_stream)
        return {}

    @staticmethod
    def parse_package_json(file_stream):
        data = file_stream.read()
        if data.startswith(codecs.BOM_UTF8):
            encoded_data = data.decode('utf-8-sig')
        else:
            encoded_data = data.decode('utf-8')
        return json.loads(encoded_data)
