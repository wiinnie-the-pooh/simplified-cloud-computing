#!/usr/bin/env python


#--------------------------------------------------------------------------------------
import os
RACKSPACE_USER = os.getenv( "RACKSPACE_USER" )
RACKSPACE_KEY = os.getenv( "RACKSPACE_KEY" )


#--------------------------------------------------------------------------------------
import cloudfiles

a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
for a_container_name in a_cloudfiles_conn.list_containers() :
    a_cloudfiles_container = a_cloudfiles_conn[ a_container_name ]
    an_objects = a_cloudfiles_container.get_objects()
    [ a_cloudfiles_container.delete_object( an_object ) for an_object in an_objects ]
    a_cloudfiles_conn.delete_container( a_cloudfiles_container ) 
    pass


#--------------------------------------------------------------------------------------
from libcloud.types import Provider 
from libcloud.providers import get_driver 

Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
[ node.destroy() for node in a_libcloud_conn.list_nodes() ]


#--------------------------------------------------------------------------------------
print "OK"


#--------------------------------------------------------------------------------------
