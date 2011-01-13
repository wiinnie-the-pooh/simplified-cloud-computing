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
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e


#--------------------------------------------------------------------------------------
def calculate_speed( the_size, the_time ):
    import sys
    if the_time < 0:
       return 0
       
    a_speed = ( float( the_size * 8 ) / the_time ) / 1024

    return a_speed


#--------------------------------------------------------------------------------------
def get_testing_bucket( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, the_region ):
    a_bucket_name="download-seed-size"
    import hashlib
    a_bucket_name = hashlib.md5( a_bucket_name + the_region ).hexdigest()

    from boto.s3.connection import S3Connection
    a_conn = S3Connection( aws_access_key_id = AWS_ACCESS_KEY_ID, 
                           aws_secret_access_key = AWS_SECRET_ACCESS_KEY )
    a_bucket = a_conn.get_bucket( a_bucket_name )
    
    return a_bucket


#--------------------------------------------------------------------------------------
class SeedSizeMesurement :
    #------------------------------------------------------------------------------------
    def __init__( self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, the_region, the_number_threads, the_initial_size = 8192 ) :
        #---------------------------- Adjust 'boto' functionality -----------------------------
        import ConfigParser
        a_config_parser = ConfigParser.SafeConfigParser()
        a_config_parser.add_section( 'Boto' )
        a_config_parser.set( 'Boto', 'num_retries', '0' )

        import tempfile
        self._config_file = tempfile.mkstemp()[ 1 ]
        a_boto_config = open( self._config_file, 'w' )
        a_config_parser.write( a_boto_config )
        a_boto_config.close()

        import os
        os.environ[ 'BOTO_CONFIG' ] = self._config_file

        #------------------------------ Get a testing bucket -------------------------------
        self._bucket = get_testing_bucket( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, the_region )
        self._values = list()
        dummy = [self._values.append( int( a_key.name ) ) for a_key in self._bucket if a_key.name != "values" ]
        
        #---------------------------- Estimate the timeout value ------------------------------
        self._timeout = measure_download_time( self._bucket, self._values, the_initial_size )
        print_d( "timeout (true) = %3.2f, sec\n" % ( self._timeout ) )

        self.set_number_threads( the_number_threads )
        pass


    #------------------------------------------------------------------------------------
    def timeout( self ):
        return self._timeout


    #------------------------------------------------------------------------------------
    def set_number_threads( self, the_value ):
        self._number_threads = the_value
        a_timeout = self._timeout * self._number_threads
        print_d( "timeout (efficient) = %3.2f, sec\n" % ( a_timeout ) )

        import socket
        socket.setdefaulttimeout( a_timeout )
        
        pass
    
    #------------------------------------------------------------------------------------
    def number_threads( self ):
        return self._number_threads
    
    #------------------------------------------------------------------------------------
    def __call__( self, the_filesize ):
      if self._number_threads == 1:
         a_time = measure_download_time( self._bucket, self._values, the_filesize )
         a_speed = calculate_speed( the_filesize, a_time )
         return a_speed
      
      
      from cloudflu.common import WorkerPool
      import time
      a_start_time = time.time()

      a_worker_pool = WorkerPool( self._number_threads )
      for i in range( self._number_threads ):
          a_worker_pool.charge( measure_download_time, ( self._bucket, self._values, the_filesize ) )
          pass
      
      a_times = a_worker_pool.get_results()
      a_worker_pool.shutdown()

      an_end_time = time.time()
      a_time = an_end_time - a_start_time
      a_speeds = list()
      a_string = ''
      for time in a_times:
          a_speed = calculate_speed( the_filesize, time )
          a_speeds.append( a_speed )
          a_string += " %4.2f " % time
          pass
      
      a_count_non_zero = self._number_threads - a_speeds.count( 0 )
      a_speed = ( ( float( a_count_non_zero ) * the_filesize * 8 ) / float( a_time ) ) / 1024
      print_d( "%4d - {%s} : %4.2f = %4.2f\n" % ( the_filesize, a_string, a_time, a_speed ) )
      
      return a_speed
      
    
    #------------------------------------------------------------------------------------
    def __del__( self ) :
        import os; os.remove( self._config_file )
        #print '__del__'
        pass
    pass



#--------------------------------------------------------------------------------------
def get_key_name( the_values, the_filesize ):
    if the_values.count( the_filesize ) != 0 or len( the_values ) == 0:
       a_key_name = str( the_filesize )
       return a_key_name
    
    the_values.append( the_filesize )
    the_values.sort()
    an_index = the_values.index( the_filesize )
    a_left_value = the_values[ an_index - 1 ]
    a_right_value = the_values[ an_index + 1 ]
    the_values.remove( the_filesize )
    
    # if the_filesize less than first value( 8192 ), we return first value
    if an_index == 0: 
       a_key_name = str ( the_values[ an_index ] )
       return a_key_name
       pass
    
    if ( the_filesize - a_left_value ) >= ( a_right_value - the_filesize ):
       a_key_name = str ( a_right_value )
       pass
    else:
       a_key_name = str ( a_left_value )
       pass
    
    
    return a_key_name


#--------------------------------------------------------------------------------------
def measure_download_time( the_bucket, the_values, the_filesize ):
    a_key_name = get_key_name( the_values, the_filesize )

    from boto.s3.key import Key
    a_key=Key( the_bucket, a_key_name )
    import tempfile
    a_file = tempfile.mkstemp( prefix = '%d-' % the_filesize )[ 1 ]
    import time
    a_time = -1
    try:
       a_begin_time=time.time()
       a_key.get_contents_to_filename( a_file )
       a_end_time=time.time()
       a_time = a_end_time - a_begin_time
       pass
    except Exception, exc:
       pass
    import os
    os.system( 'rm %s' %a_file )
    return a_time
    

#--------------------------------------------------------------------------------------
def search_best_region( the_nb_attempts, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY ):
    print_d( "looking for \"best\" region ...\n" )
    a_regions = [ '', 'EU', 'ap-southeast-1', 'us-west-1' ]
    
    a_test_filesize = 8192
    
    # Prepare buckets in different regions and dictionary for speed values 
    a_region2bucket = {}
    a_region2speeds = {}    
    a_region2sum_speeds= {}
    for a_region in a_regions:
        a_region2bucket[ a_region ] = get_testing_bucket( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, a_region  )
        a_region2speeds[ a_region ] = list()
        a_region2sum_speeds[ a_region ] = 0
        pass
    
    for i in range( the_nb_attempts ):
        for a_region in a_regions:
            a_time = measure_download_time( a_region2bucket[ a_region ], list(), a_test_filesize )
            a_speed  = calculate_speed( a_test_filesize, a_time )
            a_region2speeds[ a_region ].append( a_speed )
            a_region2sum_speeds[ a_region ] = a_region2sum_speeds[ a_region ] + a_speed
            pass
        pass    
    
    # Calculate average speed in each region and delete buckets
    average_speed2region = {}
    for a_region in a_regions:
        an_averagespeed = a_region2sum_speeds[ a_region ] / float( the_nb_attempts )
        average_speed2region[ an_averagespeed ] = a_region
        print_d( " region \'%s\' : %4.0f, kbs\n"  % ( a_region, an_averagespeed ) )
        pass
    
    an_average_speeds = average_speed2region.keys()
    an_average_speeds.sort(); an_average_speeds.reverse()
    a_best_average_speed = an_average_speeds[ 0 ]
    
    a_best_region = average_speed2region[ a_best_average_speed ]
    
    a_full_name = a_best_region
    if a_best_region == '':
       a_full_name = "us-east-1 ( \'\' )"
       pass
    
    print_d( "\nfastest region - \"%s\"\n\n" % a_full_name )

    a_first_stats = {}
    a_first_stats[ a_test_filesize ] = a_region2speeds[ a_region ] # further, we use this values
    
    return a_best_region, a_first_stats 


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
def create_values_string( the_values ) :
    a_string = ''
    for a_value in the_values:
        a_string +=  "%4.2f, " % a_value
        pass

    return a_string[ : -2 ] # remove last ", "


#--------------------------------------------------------------------------------------
def print_dict( the_x2y ) :
    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        a_values_string = create_values_string( the_x2y[ a_x ] )
        print_d( "%4d : %s\n" % ( a_x, a_values_string ) )
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
            print_d(  " + " )
        else:
            print_d( " - " )
            pass

        a_values_string = create_values_string( the_x2y[ a_x ] )
        print_d( "%4d : %s\n" % ( a_x, a_values_string ) )

        a_counter += 1
        pass
    pass


#--------------------------------------------------------------------------------------
def arithmetic_average( the_values ):
    a_size = len( the_values )
    a_summ = 0
    for a_value in the_values:
        a_summ += a_value
        pass

    an_arithmetic_average = a_summ / float( a_size )

    return an_arithmetic_average
    
    
#--------------------------------------------------------------------------------------
def get_y( the_x2y ):
    
    return arithmetic_average( the_x2y )


#--------------------------------------------------------------------------------------
def find_center( the_x2y, the_sub2_nb_attempts ) :
    an_average_y = {}

    a_xs = the_x2y.keys()
    a_nb_attempts = len( a_xs )

    a_xs.sort()
    for an_id in range( a_nb_attempts ) :
        a_center_x = a_xs[ an_id ]
        a_neighbor_nb_attemps = 0
        an_y = 0.0

        # print "[", 
        if an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += an_id
            for a_sub_id in range( an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += get_y( the_x2y[ a_x ] )
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id - the_sub2_nb_attempts, an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += get_y( the_x2y[ a_x ] )
                # print "%4d" % a_x,
                pass
            pass

        # print "| %4d |" % a_center_x,

        if a_nb_attempts - an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += a_nb_attempts - an_id
            for a_sub_id in range( an_id, a_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += get_y( the_x2y[ a_x ] )
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id, an_id + the_sub2_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += get_y( the_x2y[ a_x ] )
                # print "%4d" % a_x, 
                pass
            pass
        an_average_y[ a_center_x ] = an_y / a_neighbor_nb_attemps
        # print "] = %4d x %d" % ( an_average_y[ a_center_x ], a_neighbor_nb_attemps )

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
    print_d( "center : [ %4d ] = %4d\n\n" % ( a_center_x, a_max_average_y ) )
    
    return a_center_x, a_max_average_y


#--------------------------------------------------------------------------------------
def update_x2y( the_fun, the_x2y, the_x ) :
    an_y = the_fun( the_x )
    try:
        the_x2y[ the_x ].append( an_y )
        pass
    except:
        the_x2y[ the_x ] = [ an_y ]
        pass
    pass


#--------------------------------------------------------------------------------------
def get_stats( the_fun, the_x2y, the_cost, the_center_x, the_region_x, the_nb_attempts ) :
    a_half_area = ( the_center_x * the_region_x ) / 100.0
    a_start_x = the_center_x - a_half_area
    an_end_x = the_center_x + a_half_area

    an_area = 2.0 * a_half_area
    if a_start_x < 1.0 : # The special Amazon workaround
        a_start_x = 1000.0
        an_area = an_end_x - a_start_x
        pass

    print_d(  "[ %4d - %4d ] :\n" % ( a_start_x, an_end_x ) )

    a_sub_xs = []
    a_x = an_end_x
    a_step = an_area / float( the_nb_attempts )
    for an_id in range( the_nb_attempts + 1 ) :
        update_x2y( the_fun, the_x2y, a_x )
        a_sub_xs.append( a_x )
        the_cost += a_x * the_fun.number_threads()
        a_x -= a_step
        pass

    print2_dict( a_sub_xs, the_x2y )
    print_d( "cost : %4d\n\n" % the_cost )

    return the_x2y, the_cost, an_area


#--------------------------------------------------------------------------------------
def calculate_optimal_number_threads( the_fun, the_seed_size, the_precision, the_nb_attempts ):
    a_precision = float( the_precision / 100.0 )
    a_nb_threads = a_start_nb_threads = the_fun.number_threads()
    a_start_speed = 0.0
    a_cost = 0
    while True:
        print_d( "number threads : %d\n" % a_nb_threads )
        the_fun.set_number_threads( a_nb_threads )
        a_speed = 0.0
        for an_attempt in range( the_nb_attempts ) :
            a_speed += the_fun( the_seed_size )
            a_cost += the_seed_size * a_nb_threads
            pass
        
        a_speed /= float( the_nb_attempts )
        print_d( "speed : %4d\n\n" % a_speed )

        import math
        if a_speed < a_start_speed or math.fabs( a_speed - a_start_speed ) / a_speed < a_precision:
            an_optimize_nb_threads = a_start_nb_threads
            break

        a_start_speed = a_speed
        a_start_nb_threads = a_nb_threads
        a_nb_threads += 1
        pass
    
    the_fun.set_number_threads( an_optimize_nb_threads )
    
    return a_cost


#--------------------------------------------------------------------------------------
def calculate_optimal_seed_size( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts, the_x2y, the_get_stats = get_stats ) :
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
    print_d( "%4d - %4d\n\n" % ( a_center_x, 0.0 ) )
    a_sub_nb_attempts = the_nb_attempts / 1
    a_cost = 0.0
    a_x2y = the_x2y

    #------------------------------------------------------------------------------------------
    a_max_average_y = 0.0
    a_precision = float( the_precision / 100.0 )
    while True:
        a_max_average_y2 = a_max_average_y
        a_center_x2 = a_center_x

        a_x2y, a_cost, an_area = the_get_stats( the_fun, a_x2y, a_cost, a_center_x, the_region_x, the_nb_attempts )
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
    print_d( "solution : %4d / cost : %4d\n\n" % ( an_optimize_x, a_cost ) )

    return an_optimize_x, a_cost


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts, the_x2y, the_get_stats = get_stats ) :
    a_precision = the_precision * 3.0
    an_old_number_threads = the_fun.number_threads()
    a_cost = 0
    a_seed_size, a_cost = calculate_optimal_seed_size( the_fun, the_center_x, the_region_x, a_precision, the_nb_attempts, the_x2y, the_get_stats ) 

    a_cost += calculate_optimal_number_threads( the_fun, a_seed_size, the_precision, the_nb_attempts )
    if the_fun.number_threads() != an_old_number_threads:
       the_x2y = {}
       pass
    
    a_seed_size, a_cost2 = calculate_optimal_seed_size( the_fun, a_seed_size, the_region_x, the_precision, the_nb_attempts, the_x2y, the_get_stats )
    #a_seed_size, a_cost2 = calculate_optimal_seed_size( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts, the_x2y, the_get_stats )  
    
    a_cost += a_cost2
    return a_seed_size, a_cost


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    from cloudflu import amazon

    an_usage_description = "%prog --precision=10 --start-size=65536 --solution-window=50 --number-mesurements=5"

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    an_option_parser.add_option( "--region",
                                 metavar = "< data center region : None, 'EU', ''( us-east ), 'us-west-1' or 'ap-southeast-1' >",
                                 choices = [ 'None', 'EU', '', 'us-west-1', 'ap-southeast-1' ],
                                 action = "store",
                                 dest = "region",
                                 help = "'%default', by default, for search \"best\" region. ",
                                 default = None )    

    an_option_parser.add_option( "--number-threads",
                                 metavar = "< number of threads >",
                                 type = "int",
                                 action = "store",
                                 dest = "number_threads",
                                 help = "(%default, by default)",
                                 default = 3 )

    an_option_parser.add_option( "--precision",
                                 metavar = "< algorithm precision, % >",
                                 type = "int",
                                 action = "store",
                                 dest = "precision",
                                 help = "(%default, by default)",
                                 default = 10 )
    
    an_option_parser.add_option( "--start-size",
                                 metavar = "< start value for the search algorithm, bytes >",
                                 type = "int",
                                 action = "store",
                                 dest = "start_size",
                                 help = "(%default, by default)",
                                 default = 65536 )
    
    an_option_parser.add_option( "--solution-window",
                                 metavar = "< initial solution window considered to, %>",
                                 type = "int",
                                 action = "store",
                                 dest = "solution_window",
                                 help = "(%default, by default)",
                                 default = 50 )
                             
    an_option_parser.add_option( "--number-mesurements",
                                 metavar = "< number mesurements to be done in the solution window>",
                                 type = "int",
                                 action = "store",
                                 dest = "number_mesurements",
                                 help = "(%default, by default)",
                                 default = 5 )
    
    amazon.security_options.add( an_option_parser )

    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    a_precision = an_options.precision

    a_center_x = an_options.start_size

    a_region_x = an_options.solution_window

    a_nb_attempts = an_options.number_mesurements
    
    a_data_region = an_options.region
    
    a_nb_threads = an_options.number_threads
    
    a_stats = {}
    if a_data_region == None:
       a_data_region, a_stats = search_best_region( a_nb_attempts, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
       pass
    
    an_engine = SeedSizeMesurement( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, a_data_region , a_nb_threads )
    
    from cloudflu.common import Timer
    a_spent_time = Timer()

    an_optimize_x, a_cost = entry_point( an_engine, a_center_x, a_region_x, a_precision, a_nb_attempts, a_stats, get_stats)

#    from preferences import resource_filename; an_rcfilename = resource_filename()
#    import time; an_rcfilename_save = '%s_%s' % ( an_rcfilename, time.strftime( '%Y-%m-%d_%H:%M' ) )

#    import os; os.system( "cp %s %s" % ( an_rcfilename, an_rcfilename_save ) )

#    import os; os.system( "perl -p -i -e 's/(socket_timeout =)\s*[.0-9]+/\\1 %3.2f/' %s" % 
#                          ( an_engine.timeout(), an_rcfilename ) )

#    import os; os.system( "perl -p -i -e 's/(number_threads =)\s*[0-9]+/\\1 %d/' %s" % 
#                          ( an_engine.number_threads(), an_rcfilename ) )

#    import os; os.system( "perl -p -i -e 's/(upload_seed_size =)\s*[0-9]+/\\1 %d/' %s" % 
#                          ( an_optimize_x, an_rcfilename ) )

    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------
