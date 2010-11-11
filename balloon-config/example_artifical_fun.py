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
def calculate_optimize_value( the_logfiles, the_initial_x, the_finite_x, the_precision ):
    from artificial import function
    fun = function( the_logfiles, the_initial_x, the_finite_x )
    a_start_x = the_initial_x
    a_end_x = the_finite_x
    count_attempts = 4
    a_test_x = a_end_x
    while float( a_end_x - a_start_x ) / a_start_x > float( the_precision ) / 100 :
       an_upload_test = False 
       while not an_upload_test:
          an_upload_attempt = {}
          for i in range( 0, count_attempts ):
             an_upload_attempt[i] = fun( a_test_x )
             if i >= 1 and ( an_upload_attempt[i-1] == 0 and an_upload_attempt[ i ] == 0 ):
                break
             pass
          a_count_false = 0
          for i in range( 0, count_attempts ):
             try:             
                if an_upload_attempt[i] == 0:
                   a_count_false = a_count_false + 1
             except KeyError:   
                break
             pass
          if a_count_false >= 2: 
             a_end_x = a_test_x
             a_test_x = a_end_x -( a_end_x - a_start_x ) / 2
             pass
          else:
             an_upload_test=True
             pass
          if float( a_end_x - a_start_x ) / a_start_x < float( the_precision ) / 100:
             a_test_x=a_start_x
             break
          pass
       a_start_x = a_test_x
       a_test_x = a_end_x
       print "Start size", a_start_x
       print "End_size",  a_end_x
       
       pass
    #Testing result 
    optimize_x = a_test_x
    print "The optimize value  is " , optimize_x
    #test_result_x = optimize_x * ( 1 + float( the_precision ) / 100 )
    #print "Checking optimize + precision ", fun( test_result_x )
    #print "Checking optimize + precision ", fun( test_result_x )
    #print "Checking optimize + precision ", fun( test_result_x )
    
    return a_test_x
   

#---------------------------------------------------------------------------------------------
an_usage_description = "%prog"
an_usage_description += " ['logfile1' ['logfile2' ['logfile3'...]]] "
an_usage_description += " --initial-x=1"
an_usage_description += " --finite-x=2048"
an_usage_description += " --precision=11"


from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )


an_option_parser.add_option( "--initial-x",
                             metavar = "< The start value of the search range, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "initial_x",
                             help = "(\"%default\", by default)",
                             default = 1 )
                             
an_option_parser.add_option( "--finite-x",
                             metavar = "< The finite value  of the search range, Kbytes >",
                             type = "int",
                             action = "store",
                             dest = "finite_x",
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

a_logfiles=None
if len( an_args ) == 0 :
   a_logfiles = [ raw_input( " Enter the path to logfiles:  " ) ]
   pass
else:
   a_logfiles=an_args
   pass

import os
for a_logfile in a_logfiles:
   if not os.path.exists( a_logfile ):
      an_option_parser.error( "The given logfile should exists' \n" )
      pass
   pass

an_initial_x = an_options.initial_x

an_finite_x = an_options.finite_x

a_precision = an_options.precision

an_optimize_size = calculate_optimize_value( a_logfiles, an_initial_x, an_finite_x, a_precision )


