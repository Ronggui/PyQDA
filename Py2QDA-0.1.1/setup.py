from distutils.core import setup

setup(
    name='PyQDA',
    version='0.1.1',
	author='Colin Curtain',
	author_email='ccbogel@hotmail.com',
    packages=['PyQDA',],
    package_data={'PyQDA':['About.html','Help.html','PyQDA128.png']},
	url='http://pyqda.wordpress.com/2013/11/04/pyqda-a-beginning/',
    license='LICENSE.txt',
	description='A qualitative data analysis application',
    long_description=open('README.txt').read(),
)
