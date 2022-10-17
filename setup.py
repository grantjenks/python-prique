"""Package Setup for python-prique

Build binary extension in-place for testing with:

    $ python setup.py build_ext --inplace

Create annotations for optimization:

    $ cython -3 -a src/prique/_prique.pyx
    $ python3 -m http.server
    # Open src/prique/_prique.html in browser.
"""

import pathlib
import re

from setuptools import Extension, setup
from setuptools.command.test import test as TestCommand

from Cython.Build import cythonize


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox

        errno = tox.cmdline(self.test_args)
        exit(errno)


init = (pathlib.Path('src') / 'prique' / '__init__.py').read_text()
match = re.search(r"^__version__ = '(.+)'$", init, re.MULTILINE)
version = match.group(1)

with open('README.rst') as reader:
    readme = reader.read()

setup(
    name='prique',
    version='0.0.1',
    description='Priority queue.',
    long_description=readme,
    author='Grant Jenks',
    author_email='contact@grantjenks.com',
    url='http://www.grantjenks.com/docs/prique/',
    license='Apache 2.0',
    package_dir={'': 'src'},
    packages=['prique'],
    ext_modules=cythonize(
        [Extension('prique._core', ['src/prique/_core.py'])],
        language_level='3',
    ),
    tests_require=['tox'],
    cmdclass={'test': Tox},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
