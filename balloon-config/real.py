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
def create_boto_config():
    import os
    a_saved_environ = os.environ

    a_boto_config = './boto_cfg'
    fp=open( a_boto_config, 'w' )
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.add_section( 'Boto' )
    config.set( 'Boto', 'num_retries', '0' )
    config.write( fp )
    fp.close()

    os.environ[ 'BOTO_CONFIG' ] = a_boto_config
    return a_boto_config, a_saved_environ

#---------------------------------------------------------------------------------------
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
    a_filename='timeout_test_file'
    a_filesize=8192
    a_file = create_test_file( a_filesize )
    from boto.s3.key import Key    
    a_key=Key( the_backet, 'testing_' + a_filename )
    import time
    a_begin_time=time.time()
    #print "put data in the key "
    a_key.set_contents_from_filename( a_file )
    a_end_time=time.time()
    a_timeout = a_end_time - a_begin_time
  
    delete_object( a_key )
    sh_command( 'rm %s' % a_file )

    return a_timeout


#--------------------------------------------------------------------------------------     
def create_logfile( a_region, the_suffix, the_timeout ):
    import os
    import datetime
    a_curr_date = datetime.datetime( 1, 1, 1 ).now()
    a_date = str( a_curr_date.date() )
    a_time = str( a_curr_date.time() )[ :5 ].replace( ':', '-' )

    a_username = None
    try:
        a_username = os.getlogin()
    except:
        a_username = os.environ[ 'USER' ]
        pass

    a_filename = a_region + "_" + a_username + the_suffix + "_" + a_date + "_" + a_time \
                          + "_" + str( os.getpid() ) + "_" + "%3.3f" % the_timeout + ".csv"
    a_file = open( './logs/%s' % a_filename, 'w' )
    return a_file

#-----------------------------------------------------------------------------------------
def restore_environ( the_saved_environ, the_config_file ):
    sh_command( 'rm %s' % the_config_file )
    import os
    os.environ = the_saved_environ
    pass


#-----------------------------------------------------------------------------------------
class try_upload():
   def __init__( self, the_region, the_logsuffix ):
      from boto.s3.connection import S3Connection
      import uuid
      import os
      
      self.region = the_region
      self.a_conn=S3Connection( aws_access_key_id=os.getenv( "AWS_ACCESS_KEY_ID" ), aws_secret_access_key=os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
      a_backet_name="testing-" + str( uuid.uuid4() )
      self.backet=self.a_conn.create_bucket( a_backet_name, location=self.region )
      self.timeout = calculate_timeout( self.backet )
      import socket
      print 'The timeout in the "%s" region is "%3.2f" ' % ( self.region, self.timeout )
      socket.setdefaulttimeout( self.timeout )
      self.logfile = create_logfile( self.region, the_logsuffix, self.timeout )
      self.volumes = list()
      self.speed2volume = {}   
      pass

   
   #------------------------------------------------------------------------------------
   def save_results( self, the_size, the_speed ):
      if the_size not in self.volumes:
         self.volumes.append( the_size )
         self.speed2volume[ the_size ] = [ the_speed ]
         pass
      else:
         self.speed2volume[ the_size ].append( the_speed )
         pass
   
   #------------------------------------------------------------------------------------
   def write_results( self ):
       self.volumes.sort()
       for a_volume in self.volumes:
          self.logfile.write( str( a_volume / 1024 ) + ";" )
          for a_speed in self.speed2volume[ a_volume ]:
              self.logfile.write( str( a_speed ) + ";" )
              pass
          self.logfile.write( "\n" )
          pass
       self.logfile.close()
   
   #------------------------------------------------------------------------------------
   def __call__( self, the_size ):
      from boto.s3.key import Key
      a_key_name = 'test_' + str( the_size )
      a_key=Key( self.backet, a_key_name )
      a_file = create_test_file( the_size )
      import time
      try:
         a_begin_time=time.time()
         a_key.set_contents_from_filename( a_file )
         a_end_time=time.time()
         a_timeout = a_end_time - a_begin_time
         a_speed = ( float( the_size * 8 ) / ( a_end_time - a_begin_time ) ) / 1024
         delete_object( a_key )
         pass
      except Exception as exc:
         delete_object( a_key )
         a_speed = 0
         pass
      pass
      sh_command( 'rm %s' % a_file )
      self.save_results( the_size, a_speed )
      return a_speed

   #------------------------------------------------------------------------------------
   def __del__( self ):
      delete_object( self.backet )
      self.write_results()
      import socket
      socket.setdefaulttimeout( None )
      pass      


#------------------------------------------------------------------------------------
