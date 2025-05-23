import re

import setuptools

with open('README.md', 'r', encoding='utf8') as readme_file:
    long_description = readme_file.read()

# Inspiration: https://stackoverflow.com/a/7071358/6064135
with open('pyfamilysafety/_version.py', 'r', encoding='utf8') as version_file:
    version_groups = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_groups:
        version = version_groups.group(1)
    else:
        raise RuntimeError('Unable to find version string!')

REQUIREMENTS = [
    "aiohttp >= 3.7.0",
    "python-dateutil >= 2.7.0"
]

DEV_REQUIREMENTS = [
    'bandit >= 1.7,< 1.9',
    'black == 23.*',
    'build == 0.10.*',
    'flake8 >= 6,< 8',
    'isort >= 5,< 7',
    'mypy == 1.5.*',
    'pytest >= 7,< 9',
    'pytest-cov >= 4,< 7',
    'twine >= 4,< 7',
]

setuptools.setup(
    name='pyfamilysafety',
    version=version,
    description='Microsoft Family Safety API library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/pantherale0/pyfamilysafety',
    author='pantherale0',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={
        'pyfamilysafety': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'pyfamilysafety=pyfamilysafety:main',
        ]
    },
    python_requires='>=3.8, <4',
)