from setuptools import find_packages, setup


setup(
    name="cotidia-wsapi",
    description="REST Framework Adapter for WebSocket API.",
    version="1.0",
    author="Guillaume Piot",
    author_email="guillaume@cotidia.com",
    url="https://code.cotidia.com/cotidia/wsapi/",
    packages=find_packages(),
    package_dir={'wsapi': 'wsapi'},
    package_data={
        'cotidia.wsapi': []
    },
    namespace_packages=['cotidia'],
    include_package_data=True,
    install_requires=[
        'django>=1.10.2',
        'djangorestframework>=3.5.1'
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
)
