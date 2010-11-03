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
##
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
import boto.ec2
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import BotoServerError
import uuid
from balloon.common import sh_command
import time
import os

  
#--------------------------------------------------------------------------------------
def run_test_region ( the_region, the_file, count_crash ):
    
    a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    a_backet_name="testing-" + str( uuid.uuid4() )
    a_backet=a_conn.create_bucket( a_backet_name, location=the_region )
    a_key=Key( a_backet, 'testing_' + the_region )
    a_begin_time=time.time()
    try:
       a_key.set_contents_from_filename( the_file )
       a_end_time=time.time()
       #print "uploading time=", ( a_end_time - a_begin_time )
       a_timeout=a_end_time - a_begin_time
       print " uploading speed =", str( "%f" % ( ( ( a_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024 ) ), "kbs" 
       a_begin_time=time.time()
       a_key.get_contents_to_filename( the_file + '.out' )
       a_end_time=time.time()
       #print " downloading time =", ( a_end_time - a_begin_time ), "c"
       print " downloading speed =", str( "%f" % ( ( ( a_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024 ) ), "kbs" 
       a_key.delete()
       a_backet.delete()
       
    except Exception as exc:
       a_end_time=time.time()
       print a_end_time - a_begin_time
       print "crashed"
       a_key.delete()
       a_backet.delete()
       count_crash=count_crash + 1
       #raise exc
       a_timeout=0
       import sys, traceback
       traceback.print_exc( file = sys.stderr )
       
    return count_crash, a_timeout


#---------------------------------------------------------------------------------------------
an_usage_description = "%prog"
an_usage_description += " --socket-timeout=  , c"
an_usage_description += " --located-files= '<location-in-study-1/file-1>, <location-in-study-2/file-2>' ... "
an_usage_description += " <amazon location 1> < amazon location 2> ..."

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )


an_option_parser.add_option( "--socket-timeout",
                             metavar = "< socket timeout time >",
                             type = "int",
                             action = "store",
                             dest = "socket_timeout",
                             help = "(\"%default\", by default)",
                             default = None )

an_options, an_args = an_option_parser.parse_args()


a_S3_regions = ('EU', 'us-west-1','ap-southeast-1' )

a_regions=None
if len( an_args ) == 0 :
   a_regions = [ raw_input( " Enter the S3 region('EU', 'us-west-1','ap-southeast-1' ):  " ) ]
   pass
else:
   a_regions=an_args
   pass

a_testing_regions = list()   
for a_region in a_regions:
   if not a_region in a_S3_regions:
      an_option_parser.error( "The region must be 'EU' or 'us-west-1' or 'ap-southeast-1' \n" )
      pass
   else:
      a_testing_regions.append( a_region )
      pass
   pass



a_filename='upload_test'


for a_region in a_testing_regions:
   import socket
   if an_options.socket_timeout == None:
      a_size = 8192
      sh_command( 'dd if=/dev/zero of=timeout bs=%d count=1' % a_size , 0 )
      dummy, a_timeout=run_test_region( a_region, 'timeout', 0 )
      pass
   else:
      a_timeout = an_options.socket_timeout
   print "socket-time  in",a_region, " = ", a_timeout, ", c"
   socket.setdefaulttimeout( a_timeout )

   count_crash = 0
   for i in range( 1, 100 ):
      a_size=i*10*1024
      print "\n\ncreate testing data .... ", a_size, "bytes\n"
      sh_command( 'dd if=/dev/zero of=%s bs=%d count=1' % ( a_filename, a_size), 0 )   
      #print a_region
      count_crash, a_timeout=run_test_region( a_region, a_filename, count_crash )
      #socket.setdefaulttimeout( a_timeout )
      if count_crash > 3:
         break 
         pass
      pass
   pass      
sh_command( '%s upload_test.out' %a_filename )

