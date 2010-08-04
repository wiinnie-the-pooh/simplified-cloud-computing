#!/usr/bin/env python

# Fetching the cloud provider security cridentials
import sys
RACKSPACE_USER = sys.argv[ 1 ]
RACKSPACE_KEY = sys.argv[ 2 ]

# Creating corresponding cloudfile container
import cloudfiles
conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )

a_source_dir = sys.argv[ 3 ]
print a_source_dir

import os.path
a_container_name = os.path.basename( a_source_dir )
print a_container_name
a_container = conn.create_container( a_container_name )

a_file_object = a_container.create_object( 'dummy.txt' )
a_file_object.write( 'This is not the object you are looking for.\n' )

a_file_name = "rackspace-python-cloudfiles-1.7.2-0-gef2d5c0.zip"
a_file_object = a_container.create_object( a_file_name )
a_file_object.load_from_filename( os.path.join( a_source_dir, 'data', a_file_name ) )

