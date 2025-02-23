from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ollama_ros'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'prompt'), glob('prompt/*')),
        (os.path.join('share', package_name, 'img'), glob('img/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sobits',
    maintainer_email='ksuzuki9541@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ollama_action_server = ollama_ros.ollama_action_server:main',
            'model_downloader = ollama_ros.model_downloader:main',
        ],
    },
)
