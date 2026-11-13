from setuptools import setup, find_packages
from glob import glob

package_name = 'sally_control'

data_files = [
    ('share/ament_index/resource_index/packages',
     ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
]

config_files = glob('config/*')
if config_files:
    data_files.append(
        ('share/' + package_name + '/config', config_files)
    )

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='paola-andrea-dallos',
    maintainer_email='paoandreadallos@gmail.com',
    description='SALLY ROS 2 package',
    license='BSD-3-Clause',
    entry_points={
        'console_scripts': [],
    },
)
