from setuptools import setup, find_packages

version = '0.1'

setup(
    name='django-planet',
    version=version,
    description="A django app to create a rss planet",
    url='http://github.com/akariv/django-planet',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=['setuptools_git'],
)
