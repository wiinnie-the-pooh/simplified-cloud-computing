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
def run_test_region ( the_backet, the_file, the_count_attempts ):
    a_attemp=0
    a_bad_attemps=0.0
    while a_attemp < the_count_attempts:
       a_key=Key( the_backet, 'testing_' + str( a_attemp ) )
       try:
          a_begin_time=time.time()
          a_key.set_contents_from_filename( the_file )
          a_end_time=time.time()
          #print "uploading time=", ( a_end_time - a_begin_time )
          a_timeout = a_end_time - a_begin_time
          print " uploading speed =", str( "%f" % ( ( ( a_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024 ) ), "kbs" 
          a_key.delete()
       except Exception as exc:
          a_end_time=time.time()
          print a_end_time - a_begin_time
          print "crashed"
          a_key.delete()
          #raise exc
          #import sys, traceback
          #traceback.print_exc( file = sys.stderr )
          a_bad_attemps+=1
          print a_bad_attemps
          a_timeout = 0 # dummy timeout
          pass
       a_attemp+=1
       pass
    print "a_bad_attemps = ", a_bad_attemps
    upload_probability=  1- a_bad_attemps /the_count_attempts
    print "upload probability = ", upload_probability 

    return upload_probability, a_timeout


#---------------------------------------------------------------------------------------------
an_usage_description = "%prog"
an_usage_description += " --socket-timeout= None, c"
an_usage_description += " --located-files= '<location-in-study-1/file-1>, <location-in-study-2/file-2>' ... "
an_usage_description += " <amazon location 1> < amazon location 2> ..."
an_usage_description += " --initial-size= 1,Kbytes"
an_usage_description += " --step-size= 1,Kbytes"
an_usage_description += " --count-steps= 1"
an_usage_description += " --count-attempts= 10"

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

an_option_parser.add_option( "--initial-size",
                             metavar = "< The start value size of testing file, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "initial_size",
                             help = "(\"%default\", by default)",
                             default = 1 )
                             
an_option_parser.add_option( "--step-size",
                             metavar = "< The size of the step in bytes, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "step_size",
                             help = "(\"%default\", by default)",
                             default = 1 )

an_option_parser.add_option( "--count-steps",
                             metavar = "< The count steps >",
                             type = "int",
                             action = "store",
                             dest = "count_steps",
                             help = "(\"%default\", by default)",
                             default = 0 )

an_option_parser.add_option( "--count-attempts",
                             metavar = "< The count attempts for each file >",
                             type = "int",
                             action = "store",
                             dest = "count_attempts",
                             help = "(\"%default\", by default)",
                             default = 10 )


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

a_count_steps = an_options.count_steps 

a_step_size = an_options.step_size * 1024

an_initial_size = an_options.initial_size * 1024

a_count_attempts = an_options.count_attempts

a_filename='upload_test'


for a_region in a_testing_regions:
   a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
   a_backet_name="testing-" + str( uuid.uuid4() )
   a_backet=a_conn.create_bucket( a_backet_name, location=a_region )  
   import socket
   if an_options.socket_timeout == None:
      a_size = 8192
      sh_command( 'dd if=/dev/zero of=timeout bs=%d count=1' % a_size , 0 )
      dummy, a_timeout=run_test_region( a_backet, 'timeout', 1)
      pass
   else:
      a_timeout = an_options.socket_timeout
      pass
   print "socket-time  in",a_region, " = ", a_timeout, ", c"
   socket.setdefaulttimeout( a_timeout )

   a_upload_probability = 0
   for i in range( 0, a_count_steps ):
      a_size=an_initial_size + i * a_step_size
      print "\n\ncreate testing data .... ", a_size, "bytes\n"
      sh_command( 'dd if=/dev/zero of=%s bs=%d count=1' % ( a_filename, a_size), 0 ) 
      a_upload_probability, a_timeout=run_test_region( a_backet, a_filename, a_count_attempts  )
      if a_upload_probability == 0:
         break
      pass
   socket.setdefaulttimeout( None )
   a_backet.delete
   pass      
sh_command( '%s upload_test.out' %a_filename )

