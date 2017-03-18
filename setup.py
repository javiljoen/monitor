import setuptools

setuptools.setup(
    name='monitor',
    version='0.2.0',
    url='https://github.com/javiljoen/monitor',

    author='Jack Viljoen',
    author_email='javiljoen@users.noreply.github.com',

    description='Resource monitor for profiling processes and their subprocesses',
    long_description=open('README.rst').read(),

    packages=['monitor'],

    install_requires=[
        'click',
        'psutil>=1,<2',
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'monitor = monitor.monitor:main',
        ],
    },
)
