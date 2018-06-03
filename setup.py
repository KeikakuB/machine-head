from setuptools import setup, find_packages
setup(
    name="machine-head",
    version="0.1",
    py_modules=['machine-head'],
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['discord.py']
)
