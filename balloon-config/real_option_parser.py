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
def main():
   an_usage_description = "%prog"
   an_usage_description += " EU "
   an_usage_description += " --initial-size=1"
   an_usage_description += " --end-size=2048"
   an_usage_description += " --precision=11"
   an_usage_description += " --count-attempts=4"
   
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

   an_option_parser.add_option( "--count-attempts",
                                metavar = "< The count attempts for each file >",
                                type = "int",
                                action = "store",
                                dest = "count_attempts",
                                help = "(\"%default\", by default)",
                                default = 4 )
                                 
   an_option_parser.add_option( "--log-suffix",
                                metavar = "< Logsuffix, for 3G is none >",
                                type = "str",
                                action = "store",
                                dest = "log_suffix",
                                help = "(\"%default\", by default)",
                                default = "-3G" )


   an_options, an_args = an_option_parser.parse_args()
 
   a_S3_regions = ('EU', 'us-west-1','ap-southeast-1' )

   a_region=None
   if len( an_args ) == 0 :
      a_region = raw_input( " Enter the S3 region('EU', 'us-west-1','ap-southeast-1' ):  " )
      pass
   else:
      a_region=an_args[ 0 ]
      pass

   if not a_region in a_S3_regions:
      an_option_parser.error( "The region must be 'EU' or 'us-west-1' or 'ap-southeast-1' \n" )
      pass

   an_initial_size = an_options.initial_size * 1024

   an_end_size = an_options.end_size * 1024

   a_precision = an_options.precision

   a_logsuffix = an_options.log_suffix

   a_count_attempts = an_options.count_attempts

   return a_region, a_logsuffix, an_initial_size, an_end_size, a_precision, a_count_attempts
   
   
#--------------------------------------------------------------------------------------


