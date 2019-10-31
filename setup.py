#!/usr/bin/env python
"""Logo build script."""
from glob import glob
from os import path
from setuptools import setup
from Cython.Build import cythonize


base_dir = path.abspath(path.dirname(__file__))

with open(path.join(base_dir, 'README.md')) as desc:
    long_description = desc.read()

with open(path.join(base_dir, 'lib', 'logo', 'version.pyx')) as version:
    exec(version.read())


setup(
    name="logo",
    version=__version__,  # noqa F821
    license='MIT',
    description='A safe messaging system',
    author=__author__,  # noqa F821
    author_email=__author_email__,  # noqa F821
    long_description=long_description,  # noqa F821
    long_description_content_type='text/markdown',
    url=__url__,  # noqa F821
    # project_urls={
    #    "Bug Tracker": "https://bugs.example.com/HelloWorld/",
    #    "Documentation": "https://docs.example.com/HelloWorld/",
    #    "Source Code": "https://code.example.com/HelloWorld/",
    # }
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Handhelds/PDA\'s',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Gnome',
        'Framework :: AsyncIO',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Religion',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: File Sharing',
        'Topic :: Documentation',
        'Topic :: Internet',
        'Topic :: Religion',
        'Topic :: Security',
        'Topic :: System :: Archiving'
    ],
    zip_safe=False,
    test_suite='',
    python_requires='~=3.7',
    setup_requires=[
        'cython', 'pyinstaller', 'sphinx', 'sphinx_rtd_theme', 'kivymd'],
    install_requires=[],
    # namespace_packages=['angelos', 'eidon'],
    scripts=glob('bin/*'),
    ext_modules=cythonize(
        glob('lib/logo/**/*.pyx', recursive=True), build_dir="build")
)
