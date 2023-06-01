from setuptools import setup

setup(
      name='mcommunity',
      version='0.9',
      description='Library for working with the MCommunity directory via LDAP',
      url='https://github.com/umich-its-collab/mcommunity-tools',
      author='Maggie Davidson',
      author_email='jmaggie@umich.edu',
      packages=['mcommunity'],
      install_requires=['python-ldap==3.4.0']
)
