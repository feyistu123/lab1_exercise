import os
from glob import glob
from setuptools import setup

package_name = 'my_robot_nodes'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
     
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='feyo',
    maintainer_email='feyo@todo.todo',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turn_away = my_robot_nodes.turn_away:main',
            'rotate_server = my_robot_nodes.rotate_server:main',
            'square_driver = my_robot_nodes.square_driver:main',
            'drive_distance_server = my_robot_nodes.drive_distance_server:main',
        ],
    },
)
