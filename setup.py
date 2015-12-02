from setuptools import setup, find_packages


requirements = [
    'fedmsg',
    'fedmsg[commands]',
    'fedmsg[consumers]',
    'requests',
    'dogpile.cache',
]


with open('test-requirements.txt', 'r') as f:
    test_requirements = f.readlines()


setup(
    name='pdc-updater',
    version='0.0.1',
    description='Update the product-definition-center in response to fedmsg',
    license='GPLv2+',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/pdc-updater',
    install_requires=requirements,
    tests_require=test_requirements,
    packages=find_packages(),
    entry_points="""
    [moksha.consumer]
    updater = pdcupdater.consumer:PDCUpdater
    """,
)
