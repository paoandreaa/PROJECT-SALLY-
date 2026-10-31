from setuptools import find_packages, setup

package_name = 'sally_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='paola-andrea-dallos',
    maintainer_email='paoandreadallos@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'teleop_sally = sally_teleop.teleop_sally:main',
            'sally_teleop_pca = sally_teleop.sally_teleop_pca:main',
        ],
    },
)
