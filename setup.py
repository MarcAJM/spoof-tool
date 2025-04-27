from setuptools import setup

setup(
    name="spoof",
    version="0.1.0",
    py_modules=["spoof"],
    install_requires=["click", "scapy"],
    entry_points={
        "console_scripts": [
            "spoof = main:spoof",
        ]
    }
)