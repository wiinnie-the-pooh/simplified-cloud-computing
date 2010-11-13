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
    # To search optimize value we use "division by 2" method, in each point of we calculate F(x) "the_count_attempts" times and
    # search max F(x) * P(x)  
    # if we inside of the given precision - this is the result
    a_start_x = the_initial_x
    #we mean that in the start point the probability is 100%.
    a_FP_start_x = fun( a_start_x )
    a_cost = a_start_x
    a_end_x = the_finite_x
    count_attempts = the_count_attempts
    a_test_x = a_end_x
    while float( a_end_x - a_start_x ) / a_start_x > float( the_precision ) / float( 100 ) :
        a_count_crash = 0
        a_summ_fun_x = 0
        print "start:", a_start_x, "f(X)*P(x) = ", a_FP_start_x
        for i in range( 0, count_attempts ):
           an_attempt = fun( a_test_x )
           a_cost = a_cost + a_test_x
           a_summ_fun_x += an_attempt
           if an_attempt == 0:
              a_count_crash += 1
              pass
           pass
        a_probability_test_x = 1 - float( a_count_crash ) / float( count_attempts )
        if a_count_crash == count_attempts:
           an_average_fun_test_x = 0
           pass
        else:
           an_average_fun_test_x = a_summ_fun_x / ( count_attempts - a_count_crash )
           pass
        print "test_point:", a_test_x, "a_probability ", a_probability_test_x
        print "test_point:", a_test_x, "a_average_f(x) ", an_average_fun_test_x
        a_FP_test_x = an_average_fun_test_x * a_probability_test_x
        print "test_point:", a_test_x, "f(X)*P(x) = ", a_FP_test_x
        if a_FP_test_x > a_FP_start_x :
           a_start_x = a_test_x
           a_FP_start_x = a_FP_test_x
           pass
        else:
           a_end_x = a_test_x 
           pass
        print "-----------------------------------------------------------------------\n"
        a_test_x = a_start_x + float( a_end_x - a_start_x ) / float( 2 )
        an_optimize_x = a_start_x
        print "start point :", a_start_x
        print "end:", a_end_x
        pass
        
    #print "\nThe optimize value  is " , optimize_x
    #print "\nThe cost is ", a_cost, "kB"
    
    print count_attempts, an_optimize_x, a_cost
    return an_optimize_x
   

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


