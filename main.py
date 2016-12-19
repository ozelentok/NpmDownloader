import curio
import api
import os

async def main():
    await api.download_package('react', 'downloaded')
    #await api.download_package('redux', 'downloaded')
    #await api.download_package('bootstrap', 'downloaded')

if __name__ == '__main__':
    curio.run(main())
