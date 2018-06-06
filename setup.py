from setuptools import setup, find_packages
setup(
    name="machine_head",
    version="0.2",
    py_modules=['machine_head'],
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['discord.py', 'dateparser', 'regex'],
    entry_points='''
        [console_scripts]
        machine_head=machine_head:main
    ''',
)
