from setuptools import setup

setup(
    name="spoof-tool",
    version="0.1.0",
    py_modules=["spoof_tool"],
    install_requires=["click", "scapy"],
    entry_points={
        "console_scripts": [
            "spoof-tool = spoof_tool:main",
        ]
    }
)