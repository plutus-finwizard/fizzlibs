import setuptools

setuptools.setup(
    name='fizzlibs',
    version='1.0.3',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask==1.1.2',
        'pyyaml==5.4.1',
        'waitress==1.4.4',
        'munch==2.5.0',
        'pika==1.2.0',
        'google-cloud-pubsub==2.2.0',
        'google-auth==1.27.0',
        'mock==4.0.3'
    ],
)
