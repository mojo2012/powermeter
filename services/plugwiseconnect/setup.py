
from setuptools import find_packages, setup

VERSION = '1.0'

install_reqs = ['crcmod', 'paho-mqtt', 'pyserial', 'krak', 'plugwise']

setup(name='plugwiseconnect', 
    version=VERSION,
    description='',
    author='Matthias Fuchs',
    author_email='meister.fuchs@gmail.com',
    url='',
    license='GPL',
    packages=find_packages(),
    # py_modules=['plugwise'],
    install_requires=install_reqs,
    # scripts=['Plugwise-2.py', 'Plugwise-2-web.py'],
)

