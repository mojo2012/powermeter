
from setuptools import find_packages, setup

VERSION = '2.0'

install_reqs = ['crcmod', 'paho-mqtt', 'pyserial', 'krak', 'plugwise']

setup(name='plugwise2py', 
    version=VERSION,
    description='A server to control and log readings form Plugwise devices.',
    author='Seven Watt',
    author_email='info@sevenwatt.com',
    url='https://github.com/SevenW/Plugwise-2-py',
    license='GPL',
    packages=find_packages(),
    py_modules=['plugwise'],
    install_requires=install_reqs,
    scripts=['Plugwise-2.py', 'Plugwise-2-web.py'],
)

