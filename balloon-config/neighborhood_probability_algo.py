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
class TFilterFunctor :
    def __init__( self, the_start, the_end, the_precision = 1.0E-8 ) :
        self._precision = the_precision
        self._start = the_start
        self._end = the_end
        pass

    def __call__( self, the_x ) :
        return ( self._start - the_x ) < self._precision and ( the_x - self._end ) < self._precision
    
    pass


#--------------------------------------------------------------------------------------
def print_dict( the_x2y ) :
    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        pass
    pass


#--------------------------------------------------------------------------------------
def print2_dict( the_sub_xs, the_x2y ) :
    a_counter = 1
    an_y_integral = 0.0

    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        if a_x in the_sub_xs :
            print " + ", 
        else:
            print " - ", 
            pass
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        a_counter += 1
        pass
    pass


#--------------------------------------------------------------------------------------
def find_center( the_x2y, the_sub2_nb_attempts ) :
    an_average_y = {}

    a_xs = the_x2y.keys()
    a_nb_attempts = len( a_xs )

    a_xs.sort()
    for an_id in range( a_nb_attempts ) :
        a_center_x = a_x = a_xs[ an_id ]
        an_y = the_x2y[ a_x ]

        a_neighbor_nb_attemps = 0

        # print "[", 
        if an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += an_id
            for a_sub_id in range( an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id - the_sub2_nb_attempts, an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass

        # print "| %4d |" % a_center_x,

        if a_nb_attempts - an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += a_nb_attempts - an_id
            for a_sub_id in range( an_id, a_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id, an_id + the_sub2_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x, 
                pass
            pass
        an_average_y[ a_center_x ] = an_y / a_neighbor_nb_attemps
        # print "] = %4d" % an_average_y[ a_center_x ]

        pass

    #------------------------------------------------------------------------------------------
    # Finding out the best interval based on the corresponding average values
    a_max_average_y = 0.0
    an_average_y_index = 0
    for an_id in range( len( a_xs ) ) :
        a_x = a_xs[ an_id ]
        an_y = an_average_y[ a_x ]

        if an_y > a_max_average_y :
            an_average_y_index = an_id
            a_max_average_y = an_y
            pass

        pass

    a_center_x = a_xs[ an_average_y_index ]

    #------------------------------------------------------------------------------------------
    # Shift the 'center' to avoid mesurement of the same points
    if an_average_y_index == 0 :
        a_center_x -= ( a_xs[ an_average_y_index + 1 ] - a_xs[ an_average_y_index ] ) / 3.0
    elif an_average_y_index == a_nb_attempts - 1 :
        a_center_x += ( a_xs[ an_average_y_index ] - a_xs[ an_average_y_index - 1 ] ) / 3.0
    else:
        a_left_x = a_xs[ an_average_y_index - 1 ]
        a_right_x = a_xs[ an_average_y_index + 1 ]
        if an_average_y[ a_left_x ] < an_average_y[ a_right_x ] :
            a_center_x += ( a_right_x - a_center_x ) / 3.0
        else:
            a_center_x -= ( a_center_x - a_left_x ) / 3.0
            pass
        pass

    print "center: %4d - < value >: %4d\n" % ( a_center_x, a_max_average_y )    
    
    return a_center_x, a_max_average_y


#--------------------------------------------------------------------------------------
def get_stats( the_fun, the_x2y, the_cost, the_center_x, the_region_x, the_nb_attempts ) :
    an_end_x = the_center_x + the_region_x / 2.0
    a_start_x = the_center_x - the_region_x / 2.0
    a_region_x = the_region_x
    print "[ %4d - %4d ] : " % ( a_start_x, an_end_x )

    a_sub_xs = []
    a_x = an_end_x
    a_step = a_region_x / float( the_nb_attempts )
    for an_id in range( the_nb_attempts + 1 ) :
        if not the_x2y.has_key( a_x ) : 
            a_sub_xs.append( a_x )
            an_y = the_fun( a_x )
            the_x2y[ a_x ] = an_y
            the_cost += a_x
            pass
        a_x -= a_step
        pass

    print2_dict( a_sub_xs, the_x2y )
    print "cost : %4d\n" % the_cost

    return the_x2y, the_cost, a_region_x


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts, the_get_stats = get_stats ) :
    """The idea of this algorithm is very close to the 'interval' one; it supposes that the best value of a 
    probabilty nature function - F( x ) had better be defined through a some 'neighborhood', which could give
    more realistic representation of what is happenning in fact, not a precise point.

    This algorithm, like 'interval' one, designed in that way that it accumulates the statistics to be able 
    to make more 'proven' choice in whatever time over all the obtained results, not just currently calculated.
    So, it has good level of resistance to be caught in a local trap.
    
    Note, that the cost of F( x ) mesurement is much higher than whatever algorithmic tricks are applied over 
    the mesured results.
    
    The 'success' condition for this algorithm is when the function values on successive neighborhoods start
    differ less than the given 'precision'.

    This algorithm overcomes the initial limitation of the other two ( 'division by two' & 'interval probability' )
    in the point that it does not look for a solution within a given 'interval', instead it just starts to look
    from a given point with a given neighborhood, but can move in whatever direction and scale to reach the 'success'.
    
    As well, this algorithm is more universal in compare with 'interval' one, because it does not use any insights 
    about the possible shape and function behaviour. From this point, it could be used for any application of that 
    sort.
    
    The result for this algorithm is the central point in the most successful 'neighborhod', which would give us
    the higher combination of F( x ) * P( x ) expression.

    Attention, this algorithm will be satisfied even with low 'probability' behaviour functions, but the result 
    could be not what you are looking for. So, the best practise to use this algorithm it is to start it from a steady
    'probability'neighborhod that the algorithm will be able to distinguish the right trend ( in some ways, it works 
    like a dog; you need to give him a good hook first to make sure that he understood what you are looking for ).
    """
    a_center_x = the_center_x
    print "%4d - %4d\n" % ( a_center_x, 0.0 )
    a_sub_nb_attempts = the_nb_attempts / 1
    a_cost = 0.0
    a_x2y = {}

    #------------------------------------------------------------------------------------------
    a_max_average_y = 0.0
    a_precision = float( the_precision / 100.0 )
    while True:
        a_max_average_y2 = a_max_average_y
        a_center_x2 = a_center_x

        a_x2y, a_cost, a_region_x = the_get_stats( the_fun, a_x2y, a_cost, a_center_x, the_region_x, the_nb_attempts )
        a_center_x, a_max_average_y = find_center( a_x2y, a_sub_nb_attempts )

        if a_max_average_y < a_precision :
            continue

        import math
        if math.fabs( a_max_average_y - a_max_average_y2 ) / a_max_average_y > a_precision :
            continue

        if math.fabs( a_center_x - a_center_x2 ) / a_center_x > a_precision :
            continue

        break


    #------------------------------------------------------------------------------------------
    an_optimize_x = a_center_x
    print "solution : %4d / cost : %4d\n" % ( an_optimize_x, a_cost )

    return an_optimize_x, a_cost


#---------------------------------------------------------------------------------------------
