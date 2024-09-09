#!/usr/bin/env python3
import os

from setuptools import setup

import os
from os.path import join, dirname

from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


def get_version():
    """ Find the version of this package"""
    version_file = join(BASEDIR, 'ovos_PHAL_plugin_mk2_v6_fan_control/version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


PLUGIN_ENTRY_POINT = 'ovos-PHAL-plugin-mk2-v6-fan-control=ovos_PHAL_plugin_mk2_v6_fan_control:Mk2Rev6FanControls'
setup(
    name='ovos-PHAL-plugin-mk2-fan-control',
    version=get_version(),
    description='An OVOS PHAL plugin to control the fan on the mark2 dev kit',
    url='https://github.com/builderjer/ovos-PHAL-plugin-mk2-v6-fan-control',
    author='builderjer',
    author_email='builderjer@gmail.com',
    license='MIT',
    packages=['ovos_PHAL_plugin_mk2_v6_fan_control'],
    package_data={'': package_files('ovos_PHAL_plugin_mk2_v6_fan_control')},
    install_requires=required("requirements.txt"),
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    entry_points={'ovos.plugin.phal': PLUGIN_ENTRY_POINT}
)
