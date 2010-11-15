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
## Author : Andrey Simurzin
##


#--------------------------------------------------------------------------------------
def main():
   an_usage_description = "%prog"
   an_usage_description += " ['logfile1' ['logfile2' ['logfile3'...]]]"
   an_usage_description += " --artificial-fun=choice_fun_value"   
   an_usage_description += " --initial-x=1"
   an_usage_description += " --finite-x=2048"
   an_usage_description += " --precision=11"
   an_usage_description += " --count-attempts=4"
   
   from optparse import IndentedHelpFormatter
   a_help_formatter = IndentedHelpFormatter( width = 127 )
   
   from optparse import OptionParser
   an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )
   
   an_option_parser.add_option( "--artificial-fun",
                                metavar = "< The Artificial functor >",
                                type = "str",
                                action = "store",
                                dest = "artificial_fun",
                                help = "(\"%default\", by default)",
                                default = 'choice_fun_value' )

   an_option_parser.add_option( "--initial-x",
                                metavar = "< The start value of the search range, Kbytes >",
                                type = "int",
                                action = "store",
                                dest = "initial_x",
                                help = "(taken from the log file, by default)",
                                default = None )
                             
   an_option_parser.add_option( "--finite-x",
                                metavar = "< The finite value of the search range, Kbytes >",
                                type = "int",
                                action = "store",
                                dest = "finite_x",
                                help = "(taken from the log file, by default)",
                                default = None )

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
   
   an_artificial_fun = an_options.artificial_fun
   an_expr = "from artificial import %s as a_functor"  % an_artificial_fun
   exec( an_expr )
   a_fun = a_functor( a_logfiles )
   a_start, an_end = a_fun.get_defintion_domain()

   an_initial_x = an_options.initial_x
   if an_initial_x == None :
      an_initial_x = a_start
      print "The start value = %d" % an_initial_x
      pass

   a_finite_x = an_options.finite_x 
   if a_finite_x == None :
      a_finite_x = an_end
      print "The finite value = %d" % a_finite_x
      pass

   if not a_fun.check_defintion_domain( an_initial_x, a_finite_x ) :
      print "The given region is not correct. The least x in logfiles is more " \
            "than the_initial size or the greatest x in logfiles is less than the_finite_x"
      import os; os._exit( os.EX_USAGE )
      pass

   a_precision = an_options.precision
   a_count_attempts = an_options.count_attempts

   return  a_fun, an_initial_x, a_finite_x, a_precision, a_count_attempts

#---------------------------------------------------------------------------------------------
if __name__ == '__main__':
   main()
   pass
