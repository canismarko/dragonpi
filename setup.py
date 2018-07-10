# from distutils.core import setup
from setuptools import setup

setup(
    name='DragonPi',
    version='0.1',
    author='Mark Wolfman',
    author_email='canismarko@gmail.com',
    packages=['dragonpi'],
    entry_points={
        'console_scripts': [
            'dragonpi = dragonpi.run_game:main',
        ],
    },
    url='https://github.com/canismarko/dragonpi',
    license='LICENSE',
    description='A set of python tools for administering a dungeons & dragons game on a raspberry pi',
    long_description=open('README.md').read(),
    install_requires=[
        "pynput",
        "python-vlc",
    ],
)
