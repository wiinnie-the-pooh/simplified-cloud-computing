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
def create_boto_config( the_name ):
    fp=open( the_name, 'w' )
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.add_section( 'Boto' )
    config.set( 'Boto', 'num_retries', '0' )
    config.write( fp )
    fp.close()


#--------------------------------------------------------------------------------------
def create_backet( the_region):
    #print "create conn "
    a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    a_backet_name="testing-" + str( uuid.uuid4() )
    #print "create backet"
    a_backet=a_conn.create_bucket( a_backet_name, location=the_region )
    return a_backet


#--------------------------------------------------------------------------------------     
def create_test_file( the_size ):
    a_filename='upload_test'+str( the_size )
    sh_command( 'dd if=/dev/zero of=%s bs=%d count=1' % ( a_filename, the_size ) , 0 )
    return a_filename
    

#--------------------------------------------------------------------------------------
def delete_object( the_object ):
    an_allright=False
    while not an_allright:
       try:
         the_object.delete()
         an_allright = True
       except:
         pass 
    pass


#--------------------------------------------------------------------------------------
def calculate_timeout( the_backet ):
    a_filename='timeout_test_file'
    a_filesize=8192
    a_file = create_test_file( a_filesize )
    #print "create key"
    a_key=Key( the_backet, 'testing_' + a_filename )
  
    a_begin_time=time.time()
    #print "put data in the key "
    a_key.set_contents_from_filename( a_file )
    a_end_time=time.time()
    a_timeout = a_end_time - a_begin_time
  
    delete_object( a_key )
    sh_command( 'rm %s' % a_file )
    return a_timeout

#--------------------------------------------------------------------------------------
def try_upload_file( the_backet, the_size ):
    a_key_name = 'test_' + str( the_size )
    a_key=Key( the_backet, a_key_name )
    a_file = create_test_file( the_size )
    #print "try : ", the_size, "bytes"
    try:
       a_begin_time=time.time()
       a_key.set_contents_from_filename( a_file )
       a_end_time=time.time()
       #print "uploading time=", ( a_end_time - a_begin_time )
       a_timeout = a_end_time - a_begin_time
       a_speed = ( float( the_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024
       #print " uploading speed =", str( "%5d" % a_sp ) ), "kbs" 
       print the_size, " ",a_speed
       delete_object( a_key )
       sh_command( 'rm %s' % a_file )
       return True
    except Exception as exc:
       print the_size," crash"
       delete_object( a_key )
       sh_command( 'rm %s' % a_file )
       return False
    pass

#--------------------------------------------------------------------------------------
def calculate_optimize_seed( the_backet, the_initial_size, the_end_size, the_precision ):
    a_start_size = the_initial_size
    a_end_size = the_end_size
    count_attempts = 4
    a_test_size = a_end_size
    while float( a_end_size - a_start_size ) / a_start_size > float( the_precision ) / 100 :
       an_upload_test = False 
       while not an_upload_test:
          an_upload_attempt = {}
          for i in range( 0, count_attempts ):
             an_upload_attempt[i] = try_upload_file( the_backet, a_test_size )
             if i >= 1 and ( not an_upload_attempt[i-1] and not an_upload_attempt[ i ] ):
                break
             pass
          a_count_false = 0
          for i in range( 0, count_attempts ):
             try:             
                if not an_upload_attempt[i]:
                   a_count_false = a_count_false + 1
             except KeyError:   
                break
             pass
          if a_count_false >= 2: 
             a_end_size = a_test_size
             a_test_size = a_end_size -( a_end_size - a_start_size ) / 2
             pass
          else:
             an_upload_test=True
             pass
          if float( a_end_size - a_start_size ) / a_start_size < float( the_precision ) / 100:
             a_test_size=a_start_size
             break
          pass
       a_start_size = a_test_size
       a_test_size = a_end_size
       print "Start size", a_start_size
       print "End_size",  a_end_size
       
       pass
    #Testing result 
    optimize_seed = a_test_size
    
    test_result_size = optimize_seed * ( 1 + float( the_precision ) / 100 )
    print "Upload optimize + precision ", try_upload_file( the_backet, test_result_size )
    print "Upload optimize + precision ", try_upload_file( the_backet, test_result_size )
    print "Upload optimize + precision ", try_upload_file( the_backet, test_result_size )
    
    return a_test_size
   

#---------------------------------------------------------------------------------------------
import os
a_saved_environ = os.environ
a_boto_config = './boto_cfg'
create_boto_config( a_boto_config )
os.environ[ 'BOTO_CONFIG' ] = a_boto_config


#---------------------------------------------------------------------------------------------
import boto.ec2
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import BotoServerError
import uuid
from balloon.common import sh_command
import time
import os


import time

an_usage_description = "%prog"
an_usage_description += " 'EU' 'us-west-1' 'ap-southeast-1' "
an_usage_description += " --initial-size=1"
an_usage_description += " --end-size=2048"
an_usage_description += " --precision=11"


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
                             metavar = "< The start size in the search range, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "initial_size",
                             help = "(\"%default\", by default)",
                             default = 1 )
                             
an_option_parser.add_option( "--end-size",
                             metavar = "< The end size in the search range, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "end_size",
                             help = "(\"%default\", by default)",
                             default = 2048 )

an_option_parser.add_option( "--precision",
                             metavar = "< The precision, % >",
                             type = "int",
                             action = "store",
                             dest = "precision",
                             help = "(\"%default\", by default)",
                             default = 11 )


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

an_initial_size = an_options.initial_size * 1024

an_end_size = an_options.end_size * 1024

a_precision = an_options.precision

for a_region in a_testing_regions:
   a_time=time.time()
   a_backet = create_backet( a_region )
   a_timeout = calculate_timeout( a_backet )
   print "The timeout in \"%s\" region is " %a_region, a_timeout
   print "Time : ",  time.time() - a_time
   import socket
   socket.setdefaulttimeout( a_timeout )
   
   an_optimize_size = calculate_optimize_seed( a_backet, an_initial_size, an_end_size, a_precision )
   delete_object( a_backet )
   print "Time: ", time.time() - a_time
   print an_optimize_size

   pass

sh_command( 'rm %s' % a_boto_config )
os.environ = a_saved_environ 
