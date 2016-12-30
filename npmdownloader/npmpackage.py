import codecs
import json
import re
import tarfile

class NpmPackage:

    PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')

    __slots__ = ('name', 'version', 'file_path')

    def __init__(self, name: str, version: str, file_path: str):
        self.name = name
        self.version = version
        self.file_path = file_path

    def get_dependencies(self) -> dict:
        package_info = self.get_package_json()
        if 'dependencies' not in package_info:
            return {}
        return package_info['dependencies']

    def get_package_json(self) -> dict:
        with tarfile.open(self.file_path, 'r:gz') as tar_file:
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
