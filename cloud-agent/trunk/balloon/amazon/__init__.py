

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
def update_option_parser( the_option_parser ) :
    the_option_parser.add_option( "--aws-access-key-id",
                                  metavar = "< Amazon key id >",
                                  action = "store",
                                  dest = "aws_access_key_id",
                                  help = "(${AWS_ACCESS_KEY_ID}, by default)",
                                  default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
    the_option_parser.add_option( "--aws-secret-access-key",
                                  metavar = "< Amazon secret key >",
                                  action = "store",
                                  dest = "aws_secret_access_key",
                                  help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                                  default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    pass


#--------------------------------------------------------------------------------------
