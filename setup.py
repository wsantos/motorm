from setuptools import setup
import sys

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Development Status :: 4 - Beta
Natural Language :: English
Programming Language :: Python :: 2.7
Operating System :: MacOS :: MacOS X
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
"""

description = 'Synchronization primitives for Tornado coroutines.'

long_description = open("README.rst").read()

major, minor = sys.version_info[:2]

kwargs = {}
if major >= 3:
    kwargs['use_2to3'] = True

packages = ['motorm']
if "nosetests" in sys.argv:
    packages.append('test')

setup(name='motorm',
      version='0.1',
      packages=packages,
      description=description,
      long_description=long_description,
      author='Waldecir Santos',
      author_email='waldecir@gmail.com',
      url='http://github.com/wsantos/motorm/',
      install_requires=['tornado >= 3'],
      license='http://www.apache.org/licenses/LICENSE-2.0',
      classifiers=filter(None, classifiers.split('\n')),
      keywords='tornado motor mongodb mongo orm',
      # use python setup.py nosetests to test
      setup_requires=['nose','motor','schematics'],
      **kwargs
)

