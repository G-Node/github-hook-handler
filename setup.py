from setuptools import setup

__author__ = 'Achilleas Koutsou'


with open('README.md') as f:
    description_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()


classifiers = [
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 3.7',
    'Framework :: Flask'
]


setup(
    name='ghooklistener',
    version="0.1",
    author="Achilleas Koutsou",
    author_email="achilleas.k@gmail.com",
    url=None,
    description=None,
    long_description=description_text,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    license='BSD',
    packages=['ghooklistener'],
    scripts=[],
    install_requires=['Flask'],
    package_data={'ghooklistener': [license_text, description_text]},
    include_package_data=True,
    zip_safe=False,
)
