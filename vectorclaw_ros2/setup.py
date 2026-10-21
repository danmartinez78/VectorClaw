from setuptools import find_packages, setup
import os
from glob import glob

package_name = "vectorclaw_ros2"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Install any launch files if present
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="VectorClaw Contributors",
    maintainer_email="placeholder@example.com",
    description="ROS2 bridge for the Anki Vector robot via VectorClaw",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "vectorclaw_node = vectorclaw_ros2.vector_node:main",
        ],
    },
)
