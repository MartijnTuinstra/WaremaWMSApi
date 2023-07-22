from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'An api for controlling a Warema WMS system'
LONG_DESCRIPTION = 'Local api control for substituting the Warema WMS WebControl Pro'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="WaremaWMSApi", 
        version=VERSION,
        author="M. Tuinstra",
        author_email="md.tuinstra@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            'requests'
        ], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Warema WMS'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS",
            "Operating System :: Microsoft",
            "Operating System :: POSIX :: Linux"
        ]
)