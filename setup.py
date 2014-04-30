#! /usr/bin/env python

from distutils.core import setup

setup(
    name = 'Amoco',
    version = '2.x',
    packages=['amoco','amoco/arch','amoco/system','amoco/cas',
              'amoco/arch/x86',
              'amoco/arch/arm',
              'amoco/arch/arm/v7',
              'amoco/arch/arm/v8',
              'amoco/arch/sparc',
             ],
    # Metadata
    author = 'Axel Tillequin',
    author_email = 'bdcht3@gmail.com',
    description = 'yet another binary analysis framework',
    license = 'GPLv2',
    url = 'https://github.com/bdcht/amoco',
)
