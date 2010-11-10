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
def sh_command( the_command ) :
    "Execution of shell command"
    from subprocess import Popen,PIPE
    import os
    a_pipe = Popen( the_command, stdout = PIPE, stderr = PIPE, shell = True )

    a_return_code = os.waitpid( a_pipe.pid, 0 )[ 1 ]

    if a_return_code != 0 :
        os._exit( os.EX_USAGE )
        pass
    
#---------------------------------------------------------------------------------------
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
    from boto.s3.connection import S3Connection
    import os, uuid
    #print "create conn "
    a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    a_backet_name="testing-" + str( uuid.uuid4() )
    #print "create backet"
    a_backet=a_conn.create_bucket( a_backet_name, location=the_region )
    return a_backet


#--------------------------------------------------------------------------------------     
def create_test_file( the_size ):
    a_filename='upload_test'+str( the_size )
    sh_command( 'dd if=/dev/zero of=%s bs=%d count=1' % ( a_filename, the_size ) )
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
    from boto.s3.key import Key
    import time
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


#---------------------------------------------------------------------------------------
def try_upload_file( the_backet, the_size, the_count_attempts, the_logfile ):
    from boto.s3.key import Key
    a_key_name = 'test_' + str( the_size )
    a_key=Key( the_backet, a_key_name )
    a_file = create_test_file( the_size )
    a_count=0
    a_results=""
    import time
    while a_count < the_count_attempts:
       try:
          a_begin_time=time.time()
          a_key.set_contents_from_filename( a_file )
          a_end_time=time.time()
          a_timeout = a_end_time - a_begin_time
          a_speed = ( float( the_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024
          print "attempt:",a_count, "   speed = ", a_speed
          a_results = a_results + "%5.3f" % a_speed + ";"
          delete_object( a_key )
          pass
       except Exception as exc:
          print "attempt:", a_count, "   crash"
          a_results = a_results + str( 0 ) + ";"
          delete_object( a_key )
          pass
       a_count +=1
       pass
    sh_command( 'rm %s' % a_file )
    the_logfile.write( str( the_size / 1024 ) + ";" + a_results + "\n" )
    return a_results  


#-----------------------------------------------------------------------------------------
def create_logfile( a_region, the_suffix, the_timeout ):
    import os
    import datetime
    a_curr_date = datetime.datetime(1,1,1).now()
    a_date = str( a_curr_date.date() )
    a_time = str( a_curr_date.time() )[:5].replace(':','-')
    a_filename = a_region + "_" + os.getlogin() + the_suffix + "_" + a_date + "_" + a_time \
                          + "_" + str( os.getpid() ) + "_" + "%3.3f" % the_timeout + ".csv"
    a_file = open( './logs/%s' % a_filename, 'w' )
    return a_file


#-----------------------------------------------------------------------------------------
def main():
    
    import os
    a_saved_environ = os.environ
    a_boto_config = './boto_cfg'
    create_boto_config( a_boto_config )
    os.environ[ 'BOTO_CONFIG' ] = a_boto_config
    
    an_usage_description = "%prog"
    an_usage_description += " EU us-west-1 ap-southeast-1"
    an_usage_description += " --initial-size=10"
    an_usage_description += " --step-size=10"
    an_usage_description += " --count-steps=10"
    an_usage_description += " --count-attempts=10"
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
                                  default = 10 )
                              
    an_option_parser.add_option( "--step-size",
                                 metavar = "< The size of the step in bytes, Kbytes >",
                                 type = "int",
                                 action = "store",
                                dest = "step_size",
                                 help = "(\"%default\", by default)",
                                 default = 10 )
 
    an_option_parser.add_option( "--count-steps",
                                 metavar = "< The count steps >",
                                 type = "int",
                                 action = "store",
                                dest = "count_steps",
                                 help = "(\"%default\", by default)",
                                 default = 10 )
   
    an_option_parser.add_option( "--count-attempts",
                                 metavar = "< The count attempts for each file >",
                                 type = "int",
                                 action = "store",
                                 dest = "count_attempts",
                                 help = "(\"%default\", by default)",
                                 default = 10 )
                                 
    an_option_parser.add_option( "--log-suffix",
                                 metavar = "< Logsuffix, for 3G is none >",
                                 type = "str",
                                 action = "store",
                                 dest = "log_suffix",
                                 help = "(\"%default\", by default)",
                                 default = "-3G" )

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

    a_logsuffix = an_options.log_suffix

    a_count_steps = an_options.count_steps 
    a_step_size = an_options.step_size * 1024
    an_initial_size = an_options.initial_size * 1024
    a_count_attempts = an_options.count_attempts
    import socket
    for a_region in a_testing_regions:
        print "Testing %s region" % a_region
        a_backet = create_backet( a_region )
        a_timeout = calculate_timeout( a_backet )
        a_logfile = create_logfile( a_region, a_logsuffix, a_timeout )
        
        socket.setdefaulttimeout( a_timeout )
        for i in range( 0, a_count_steps ):
            a_size=an_initial_size + i * a_step_size
            print "Try upload %d bytes" % a_size 
            a_res = try_upload_file( a_backet, a_size, a_count_attempts, a_logfile )
            pass
        delete_object( a_backet )        
        pass
    os.environ = a_saved_environ
    
    pass
   
#--------------------------------------------------------------------------------------------------------------
if __name__=="__main__":
   main()
   pass
