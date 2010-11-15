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
   # It is the base class for all artifical functions ( classes )
   def __init__( self, the_logfiles ):
      #We read the_logfiles and for all values x from the logfile, we calculate probability 
      from random import SystemRandom
      self.random_entity = SystemRandom()
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
      #clculate probability for all x_values
      self.probability2x = {}
      for a_x in self.x_values:
         a_fun_values = self.list_fun_values[ a_x ]
         a_count_crash = a_fun_values.count( '0' )
         a_count_value = len( a_fun_values )
         a_probability = 1 - float( a_count_crash ) / float( a_count_value )
         self.probability2x[ a_x ] = a_probability
      pass


   #------------------------------------------------------------------------------------
   def get_defintion_domain( self ) :
      return self.x_values[ 0 ], self.x_values[ -1 ]

      
   #------------------------------------------------------------------------------------
   def check_defintion_domain( self, the_initial_x, the_finite_x ) :
      if self.x_values[ 0 ] > the_initial_x or self.x_values[ -1 ] < the_finite_x :
         return False
      
      return True


   #------------------------------------------------------------------------------------
   def linear_approximation( self, the_function, the_x, the_random_value ):
      #returns f(x) if x is in the x_values or linear interpolated f(x)
      #if the_x is not in the table of x_values, we search x1,x2 that x1 < x < x2
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
         a_fun_x1 = the_function( a_x1, the_random_value )
         a_probability_x2 = self.probability2x[ a_x2 ]
         a_fun_x2 = the_function( a_x2, the_random_value )
         # calculate f(x) and probability, using linear  approximation
         a_probability_x = ( a_probability_x1 * ( a_x2 - the_x ) + a_probability_x1 * ( the_x - a_x1 ) ) / ( a_x2 - a_x1 )
         a_fun_x = ( a_fun_x1 * ( a_x2 - the_x ) + a_fun_x2 * ( the_x - a_x1 ) ) / ( a_x2 - a_x1 )
      # If the_x is in the table of x_values , we return f(x) and probability p(x)
      else:
         a_fun_x = the_function( the_x, the_random_value )
         a_probability_x = self.probability2x[ the_x ]
         pass

      return a_fun_x, a_probability_x
   
     
#------------------------------------------------------------------------------------
class arithmetic_average( function ):
   # Using arithmetic average values to return f(x) 
   def __init__( self, the_logfiles ):
      function.__init__( self, the_logfiles )
      self.arithmetic_average_fun_value2x ={}
      for a_x in self.x_values:
         a_fun_values = self.list_fun_values[ a_x ]
         a_count_crash = a_fun_values.count( '0' )
         a_count_value = len( a_fun_values )
         a_summ_fun_value = 0.0
         for a_value in a_fun_values:
             if a_value != '0':
                a_summ_fun_value = a_summ_fun_value + float( a_value )
                pass
             pass
         if a_count_value != a_count_crash:
            an_arithmeticmetic_average_fun_value = float( a_summ_fun_value ) / float( a_count_value - a_count_crash ) 
            pass
         else:
            an_arithmeticmetic_average_fun_value = 0
            pass
         self.arithmetic_average_fun_value2x[ a_x ] = an_arithmeticmetic_average_fun_value
      pass

   #------------------------------------------------------------------------------------
   def get_arithmetic_average_fun_value( self, the_x , the_dummy = 0 ):
       return self.arithmetic_average_fun_value2x[ the_x ]
   

   #------------------------------------------------------------------------------------
   def __call__( self, the_x ):
      #returns f(x) with the probability Px
      a_random_value = self.random_entity.random()
      a_fun_x, a_probability_x = self.linear_approximation( self.get_arithmetic_average_fun_value, the_x, a_random_value )
     
      if a_random_value < a_probability_x:
         return a_fun_x
      else:
         return 0


#--------------------------------------------------------------------------------------
class normal_distribution( arithmetic_average ):
    #using normal distributed value to return f(x)
   def __init__( self, the_logfiles ):
      arithmetic_average.__init__( self, the_logfiles )
      from math import sqrt
      #dictionary for rms( root mean square )
      self.rms_fun_value2x ={}
      #dictionary for standart deviation
      self.std_deviation = {}
      for a_x in self.x_values:
         a_fun_values = self.list_fun_values[ a_x ]
         a_count_crash = a_fun_values.count( '0' )
         a_count_value = len( a_fun_values )
         a_summ_sqr_fun_value = 0.0
         for a_value in a_fun_values:
             if a_value != '0':
                a_summ_sqr_fun_value += pow( float( a_value ),2 )
                pass
             pass
         if a_count_value != a_count_crash:
            a_rms_fun_value = sqrt( a_summ_sqr_fun_value / float( a_count_value - a_count_crash ) )
            pass
         else:
            a_rms_fun_value = 0
            pass
         self.rms_fun_value2x[ a_x ] = a_rms_fun_value
         
         #calculate standart deviation 
         a_summ_deviation = 0
         for a_value in a_fun_values:
             if a_value != '0':
                a_summ_deviation += pow( float( a_value ) - self.get_arithmetic_average_fun_value( a_x ), 2 )
                pass
             pass
         if a_count_value != a_count_crash:
            self.std_deviation[ a_x ] = sqrt( a_summ_deviation / float( a_count_value - a_count_crash ) )
            pass
         else:
            self.std_deviation[ a_x ] = 0
            pass
         pass
      pass
   #------------------------------------------------------------------------------------
   def get_normal_distribution( self, the_x,the_random_value ):
      # return normal distributed f(x)
      
      import random
      if the_random_value <= 0.001:
         return self.rms_fun_value2x[ the_x ] - (3 +  self.random_entity.random() ) * self.std_deviation[ the_x ]
      
      if the_random_value > 0.001 and the_random_value <= ( 0.021 + 0.01 ):
         return self.rms_fun_value2x[ the_x ] - (2 +  self.random_entity.random() ) * self.std_deviation[ the_x ]
      
      if the_random_value > 0.022 and the_random_value <= ( 0.022 + 0,136 ):
         return self.rms_fun_value2x[ the_x ] - (1 +  self.random_entity.random() ) * self.std_deviation[ the_x ]

      if the_random_value > 0.158 and the_random_value <= ( 0.158 + 0,341 ):
         return self.rms_fun_value2x[ the_x ] -  self.random_entity.random() * self.std_deviation[ the_x ]
      
      if the_random_value > 0.499 and the_random_value <= ( 0.5 + 0,341 ):
         return self.rms_fun_value2x[ the_x ] +  self.random_entity.random() * self.std_deviation[ the_x ]

      if the_random_value > 0.841 and the_random_value <= ( 0.841 + 0,136 ):
         return self.rms_fun_value2x[ the_x ] + (1 +  self.random_entity.random() ) * self.std_deviation[ the_x ]
       
      if the_random_value > 0.977 and the_random_value <= ( 0.977 + 0,21 ):
         return self.rms_fun_value2x[ the_x ] + (2 +  self.random_entity.random() ) * self.std_deviation[ the_x ]

      if the_random_value > 0.998 and the_random_value <= 1:
         return self.rms_fun_value2x[ the_x ] + (3 +  self.random_entity.random() ) * self.std_deviation[ the_x ]
       
       
   #------------------------------------------------------------------------------------
   def __call__( self, the_x ):
      #returns f(x) with the probability Px
      a_random_value = self.random_entity.random()
      a_fun_x, a_probability_x = self.linear_approximation( self.get_normal_distribution, the_x, a_random_value )
      
      if a_random_value < a_probability_x:
         return a_fun_x
      else:
         return 0


#--------------------------------------------------------------------------------------
class choice_fun_value( function ):
    def __init__( self, the_logfiles ):
       function.__init__( self, the_logfiles )
       pass
       
       
    #------------------------------------------------------------------------------------   
    def choice_random_fun_value( self, the_x, dummy = 0 ):
        return float( self.random_entity.choice( self.list_fun_values[ the_x ] ) )
    

    #------------------------------------------------------------------------------------
    def __call__( self,the_x ):
       a_fun_x, a_probability_x = self.linear_approximation( self.choice_random_fun_value, the_x, 0 )
       return a_fun_x
       
       
#--------------------------------------------------------------------------------------  
