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
        
        
#--------------------------------------------------------------------------------------
def create_bucket():
    from boto.s3.connection import S3Connection
    import os, uuid
    a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    a_bucket_name="download-seed-size" + str( uuid.uuid4() )
    a_bucket=a_conn.create_bucket( a_bucket_name )
    return a_bucket


#--------------------------------------------------------------------------------------     
def create_test_file( the_size ):
    a_filename='upload_test'+str( the_size )
    sh_command( 'dd if=/dev/zero of=%s bs=%d count=1' % ( a_filename, the_size ) )
    return a_filename
    

#---------------------------------------------------------------------------------------
def upload_file( the_backet, the_size ):
    from boto.s3.key import Key
    a_key_name = str( the_size )
    a_key=Key( the_backet, a_key_name )
    a_file = create_test_file( the_size )
    a_key.set_contents_from_filename( a_file )

    pass


#-----------------------------------------------------------------------------------------
def main():
    an_usage_description = "%prog"
    an_usage_description += " --initial-size=10"
    an_usage_description += " --max-size=10"
    an_usage_description += " --step=2.5"
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

    an_option_parser.add_option( "--initial-size",
                                  metavar = "< The start value size of testing file, Kbytes >",
                                  type = "int",
                                  action = "store",
                                 dest = "initial_size",
                                  help = "(\"%default\", by default)",
                                  default = 8 )
                              
    an_option_parser.add_option( "--max-size",
                                 metavar = "< The max size Kbytes >",
                                 type = "int",
                                 action = "store",
                                dest = "max_size",
                                 help = "(\"%default\", by default)",
                                 default = 6000 )
 
    an_option_parser.add_option( "--step",
                                 metavar = "< The step in percent >",
                                 type = "float",
                                 action = "store",
                                dest = "step",
                                 help = "(\"%default\", by default)",
                                 default = 2.5 )
   
    an_options, an_args = an_option_parser.parse_args()
    
    a_step = an_options.step
    a_max_size = an_options.max_size * 1024
    an_initial_size = an_options.initial_size * 1024

    a_bucket = create_bucket()
    a_size = an_initial_size
    while a_size <= a_max_size:
         print "upload %d bytes" % a_size
         upload_file( a_bucket, a_size )
         a_size = int ( a_size / ( float( 100 - a_step ) / float( 100 ) ) )
         print a_size
         pass
    pass

   
#--------------------------------------------------------------------------------------------------------------
if __name__=="__main__":
   main()
   pass
