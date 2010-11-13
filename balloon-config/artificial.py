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
class function():
   def __init__( self, the_logfiles, the_initial_x, the_finite_x ):
      #We read the_logfiles and for all values x from the logfile, we calculate probability and arithmetic average of f(x)
      self.x_values = list()
      self.list_fun_values = {}
      for a_logfile in the_logfiles:
         a_file = open( a_logfile )
         for a_line in a_file.readlines():
             a_data = a_line.split( ";" )
             a_key = int( a_data[ :1 ][ 0 ] )
             a_values = a_data[ 1: ][ :-1 ]
             if self.list_fun_values.has_key( a_key ):
                for a_value in a_values:
                   self.list_fun_values[ a_key ].append( a_value )
                   pass
                pass
             else:
                self.list_fun_values[ a_key ] = a_values
                self.x_values.append( a_key )
                pass
             pass
         a_file.close()
         pass
      self.x_values.sort()

      if self.x_values[ 0 ] > the_initial_x or self.x_values[ -1 ] < the_finite_x :
         raise ValueError( "The given region is not correct. The least x in logfiles is more " + \
                            "than the_initial size or the greatest x in logfiles is less than the_finite_x " )
      self.probability2x = {}
      self.fun_value2x ={}
      for a_x in self.x_values:
         a_fun_values = self.list_fun_values[ a_x ]
         a_count_crash = a_fun_values.count( '0' )
         a_count_value = len( a_fun_values )
         a_probability = 1 - float( a_count_crash ) / float( a_count_value )
         a_summ_fun_value = 0.0
         for a_value in a_fun_values:
             if a_value != '0':
                a_summ_fun_value = a_summ_fun_value + float( a_value )
                pass
             pass
         if a_count_value != a_count_crash:
            an_average_fun_value = a_summ_fun_value / ( a_count_value - a_count_crash )
            pass
         else:
            an_average_fun_value = 0
            pass
         self.probability2x[ a_x ] = a_probability
         self.fun_value2x[ a_x ] = an_average_fun_value
         
         pass
      pass
      
      
   #------------------------------------------------------------------------------------
   def fun_linear_approximation( self, the_x ):
      # return f( x )( using  linear_approximation ) and probability for x

      #If the_x is not  in the table, we search the a_x1 and a_x2 that  a_x1 < the_x < a_x2 and 
      if the_x not in self.x_values: 
         a_x1 = 0
         a_x2 = 0
         for a_x in self.x_values:
            if the_x > a_x:
               a_x1 = a_x
               pass
            else:
               a_x2 = a_x
               break
            pass
         a_probability_x1 = self.probability2x[ a_x1 ]
         a_fun_x1 = self.fun_value2x[ a_x1 ]
         a_probability_x2 = self.probability2x[ a_x2 ]
         a_fun_x2 = self.fun_value2x[ a_x2 ]
         # calculate f(x) and probability, using linear  approximation
         a_probability_x = ( a_probability_x1 * ( a_x2 - a_x ) + a_probability_x1 * ( a_x - a_x1 ) ) / ( a_x2 - a_x1 )
         a_fun_x = ( a_fun_x1 * ( a_x2 - a_x ) + a_fun_x2 * ( a_x - a_x1 ) ) / ( a_x2 - a_x1 )
      # If the_x is in the table of x_values , we return f(x) and probability p(x)
      else:
         a_fun_x = self.fun_value2x[ the_x ]
         a_probability_x = self.probability2x[ the_x ]
         pass
      return a_fun_x, a_probability_x
   
   #------------------------------------------------------------------------------------
   def __call__( self, the_x ):
      #returns f(x) with the probability Px
      a_fun_x, a_probability_x = self.fun_linear_approximation( the_x )
      import random
      a_random_value = random.random()
      if a_random_value < a_probability_x:
         return a_fun_x
      else:
         return 0
   
#--------------------------------------------------------------------------------------
