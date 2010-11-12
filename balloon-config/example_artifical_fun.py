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
def calculate_optimize_value( fun, the_initial_x, the_finite_x, the_precision, the_count_attempts ):
    # To search optimize value we use binary search, in each point of we calculate f(x) "count_attempts" times
    # if function returns "zero" ( "count_attempts" / 2 ) times, we pass to the following point.
    # if the function returns "non-zero value" "count_attempt" times, it point becomes the initial
    # point if our range an all try again.
    # if we inside of the given precision - this is the result
    a_start_x = the_initial_x
    a_end_x = the_finite_x
    count_attempts = the_count_attempts
    a_test_x = a_end_x
    a_cost = 0
    while float( a_end_x - a_start_x ) / a_start_x > float( the_precision ) / float( 100 ) :
       a_test = False 

       while not a_test:
          an_attempt = {}
          a_count_false = 0
          for i in range( 0, count_attempts ):
             an_attempt[i] = fun( a_test_x )
             a_cost = a_cost + a_test_x
             if an_attempt[i] == 0:
                a_count_false = a_count_false + 1
                pass
             if a_count_false > ( count_attempts / 2 ):
                break
             pass
          if a_count_false > ( ( count_attempts ) / 2 ): 
             a_end_x = a_test_x
             a_test_x = a_end_x -( a_end_x - a_start_x ) / float( 2 )
             pass
          else:
             a_test=True
             pass
          if float( a_end_x - a_start_x ) / a_start_x < float( the_precision ) / float( 100 ):
             a_test_x=a_start_x
             break
          pass
       a_start_x = a_test_x
       a_test_x = a_end_x
       #print "Start size", a_start_x
       #print "End_size",  a_end_x
       
       pass
    optimize_x = a_test_x
    print "\nThe optimize value  is " , optimize_x
    print "\nThe cost is ", a_cost, "kB"
    
    return a_test_x
   

#---------------------------------------------------------------------------------------------
an_usage_description = "%prog"
an_usage_description += " ['logfile1' ['logfile2' ['logfile3'...]]] "
an_usage_description += " --initial-x=1"
an_usage_description += " --finite-x=2048"
an_usage_description += " --precision=11"
an_usage_description += " --count-attempts=4"


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

an_option_parser.add_option( "--count-attempts",
                             metavar = "< The count of calculaete f(x), % >",
                             type = "int",
                             action = "store",
                             dest = "count_attempts",
                             help = "(\"%default\", by default)",
                             default = 4 )

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
a_finite_x = an_options.finite_x
a_precision = an_options.precision
a_count_attempts = an_options.count_attempts

from artificial import function
fun = function( a_logfiles, an_initial_x, a_finite_x )
an_optimize_size = calculate_optimize_value( fun, an_initial_x, a_finite_x, a_precision, a_count_attempts )


