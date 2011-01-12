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
def create_bucket( the_region ):
    from boto.s3.connection import S3Connection
    import os, uuid
    a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    a_bucket_name="download-seed-size"
    import hashlib
    a_bucket_name = hashlib.md5( a_bucket_name + the_region ).hexdigest()
    a_bucket=a_conn.create_bucket( a_bucket_name, location = the_region )
    return a_bucket


#--------------------------------------------------------------------------------------     
def create_test_file( the_size ):
    import tempfile
    a_filename = tempfile.mkstemp( prefix = '%d-' % the_size )[ 1 ]

    import os
    os.system( 'dd if=/dev/zero of=%s bs=%d count=1 > /dev/null 2>&1' % ( a_filename, the_size ) )
    
    return a_filename
    

#---------------------------------------------------------------------------------------
def upload_file( the_backet, the_size ):
    from boto.s3.key import Key
    a_key_name = str( the_size )
    a_key=Key( the_backet, a_key_name )
    a_file = create_test_file( the_size )
    a_key.set_contents_from_filename( a_file )
    import os
    os.system( 'rm %s' % a_file )
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

    a_bucket = create_bucket( '' )
    a_size = an_initial_size
    
    a_regions = [ '', 'EU', 'ap-southeast-1', 'us-west-1' ]
    region2bucket = {}
    
    for a_region in a_regions :
        region2bucket[ a_region ] =  create_bucket( a_region )
        print "\'%s\' region - \'%s\'" %( a_region, region2bucket[ a_region ] ) 
        pass
    a_values = ""
    while a_size <= a_max_size:
         a_values += "%5d;" % a_size
         print "upload file - %d bytes" % a_size
         upload_file( region2bucket[ '' ] , a_size )
         a_size = int ( a_size / ( float( 100 - a_step ) / float( 100 ) ) )
         pass
    
    #create list of existing values 
    from boto.s3.key import Key
    a_key_name = "values"
    a_key=Key( region2bucket[ '' ], a_key_name )
    #write values w/o last ";"
    a_key.set_contents_from_string( a_values[ :-1 ] )
    
    for a_key in region2bucket[ '' ]:
        for a_region in a_regions[ 1: ]:
            print "Copying \'%s\' key to \'%s\'" %( a_key.name, a_region )
            a_new_key = a_key.copy( region2bucket[ a_region ].name, a_key.name )
            pass
        pass
    
    pass

   
#--------------------------------------------------------------------------------------------------------------
if __name__=="__main__":
   main()
   pass
