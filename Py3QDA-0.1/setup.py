from setuptools import setup

setup(
    name='Py3QDA',
    version='0.1',
	author='Ronggui Huang',
    packages=['Py3QDA'],
    package_data={'PyQDA':['About.html','Help.html','PyQDA128.png']},
    license='LICENSE.txt',
	description='A qualitative data analysis application',
    entry_points={
        'console_scripts': [
            'py3qda = Py3QDA.Py3QDA:main'
        ],
        'gui_scripts': [
            'py3qda = Py3QDA.Py3QDA:main',
        ]
    }
)
