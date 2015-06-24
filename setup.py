#!/usr/bin/env python

import os

from distutils.core import setup


def get_packages():
    base = 'PyZio'
    packages = [base]
    for d in os.listdir(base):
        dd = [base, d]
        if not os.path.isdir('/'.join(dd)):
            continue
        packages.append('.'.join(dd))
    return packages


setup(name='PyZio',
      version='0.6.0',
      description='Python Objects to handle ZIO devices',
      author='Federico Vaga, Davide Silvestri',
      author_email='federico.vaga@gmail.com, silvestridavide87@gmail.com',
      maintainer="Federico Vaga, Davide Silvestri",
      maintainer_email="federico.vaga@gmail.com, silvestridavide87@gmail.com",
      url='https://github.com/FedericoVaga/PyZio',
      packages=get_packages(),
      license='GPLv2',
)
