from setuptools import setup, find_packages

setup(
    name='optopenhash',
    version='0.1.0',
    author='Matthew Stern',
    author_email='matthew.stern@ztsystems.com',
    description=('A Python package implementing improved open‐addressing hash tables '
                 'based on the paper "Optimal Bounds for Open Addressing Without Reordering".'),
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sternma/optopenhash',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
