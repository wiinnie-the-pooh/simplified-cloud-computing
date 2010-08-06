#!/usr/bin/env python

#--------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
from distutils.core import setup, Extension

setup( name = 'balloon',
       description = 'Set of cloud computing automation utilities',
       long_description = 
       """These utilities provide seemless mode for:
        - accessing to cloud;
        - deploying user specified data and functionality to be run on this data;
        - launching of the cloud specified task;
        - storing of output data into cloud;
        - fectching of these output results from cloud;
        - other miscellaneous functions""",
       author = 'Alexey Petrov',
       author_email = 'alexey.petrov.nnov@gmail.com', 
       license = 'Apache License, Version 2.0',
       url = 'http://www.simplified-cloud-computing.org',
       platforms = [ 'linux' ],
       version = '0.5-alfa',
       classifiers = [ 'Development Status :: 3 - Alpha',
                       'Environment :: Console',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: Apache Software License',
                       'Operating System :: POSIX',
                       'Programming Language :: Python',
                       'Topic :: Scientific/Engineering',
                       'Topic :: Utilities' ],
       packages = [ 'balloon' ],
       scripts = [ 'send2cloud.py', 'fetch4queue.py', 'clean_rackspace.py', 'clean_amazon.py' ] )


#--------------------------------------------------------------------------------------
