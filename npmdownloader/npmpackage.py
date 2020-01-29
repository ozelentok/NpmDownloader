import codecs
import json
import re
import io
import tarfile
from typing import Dict, NamedTuple, Any

import aiofiles

_PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')


class NpmPackage(NamedTuple):

    name: str
    version: str
    file_path: str

    async def get_dependencies(self) -> Dict[str, Any]:
        package_info = await self.get_package_json()
        dependencies: Dict[str, Any] = {}
        if 'dependencies' in package_info:
            dependencies.update(package_info['dependencies'])
        if 'peerDependencies' in package_info:
            dependencies.update(package_info['peerDependencies'])
        return dependencies

    async def get_package_json(self) -> Dict[str, Any]:
        async with aiofiles.open(self.file_path, 'rb') as tar_file:
            tar_mem_stream = io.BytesIO(await tar_file.read())
        with tarfile.open(fileobj=tar_mem_stream, mode='r:gz') as tar_file:
            for internal_path in tar_file.getnames():
                if not _PACKAGE_JSON_PATH_PATTERN.match(internal_path):
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
