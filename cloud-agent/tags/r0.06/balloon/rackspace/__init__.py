

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
import os


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --rackspace-user=${RACKSPACE_USER} --rackspace-key=${RACKSPACE_KEY}"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--rackspace-user",
                                  metavar = "< Rackspace user >",
                                  action = "store",
                                  dest = "rackspace_user",
                                  help = "(${RACKSPACE_USER}, by default)",
                                  default = os.getenv( "RACKSPACE_USER" ) )
    
    the_option_parser.add_option( "--rackspace-key",
                                  metavar = "< Rackspace key >",
                                  action = "store",
                                  dest = "rackspace_key",
                                  help = "(${RACKSPACE_KEY}, by default)",
                                  default = os.getenv( "RACKSPACE_KEY" ) )
    pass


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    RACKSPACE_USER = the_options.rackspace_user
    if RACKSPACE_USER == None :
        print_e( "Define RACKSPACE_USER parameter through '--rackspace-user' option\n" )
        os._exit( os.EX_USAGE )
        pass

    RACKSPACE_KEY = the_options.rackspace_key
    if RACKSPACE_KEY == None :
        print_e( "Define RACKSPACE_KEY parameter through '--rackspace-key' option\n" )
        os._exit( os.EX_USAGE )
        pass

    return RACKSPACE_USER, RACKSPACE_KEY


#--------------------------------------------------------------------------------------
