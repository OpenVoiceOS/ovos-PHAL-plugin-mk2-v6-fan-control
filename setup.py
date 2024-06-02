#!/usr/bin/env python3
import os

from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


PLUGIN_ENTRY_POINT = 'ovos-PHAL-plugin-mk2-v6-fan-control=ovos_PHAL_plugin_mk2_v6_fan_control:Mk2Rev6FanControls'
setup(
    name='ovos-PHAL-plugin-mk2-fan-control',
    version='0.0.1',
    description='An OVOS PHAL plugin to control the fan on the mark2 dev kit',
    url='https://github.com/builderjer/ovos-PHAL-plugin-mk2-v6-fan-control',
    author='builderjer',
    author_email='builderjer@gmail.com',
    license='MIT',
    packages=['ovos_PHAL_plugin_mk2_v6_fan_control'],
    package_data={'': package_files('ovos_PHAL_plugin_mk2_v6_fan_control')},
    install_requires=["ovos-plugin-manager>=0.0.1",
                      "ovos-i2c-detection>=0.0.0a2"],
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
