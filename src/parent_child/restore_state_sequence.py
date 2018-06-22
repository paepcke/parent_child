#!/usr/bin/env python
'''
Created on Jun 22, 2018

@author: paepcke
'''
import argparse
import csv
import os
import sys

class StateSequenceRestorer(object):
    '''
    classdocs
    '''


    def __init__(self, in_file, out_file=None):
        '''
        Constructor
        '''
        self.csv_reader = None
        try:
            with open(in_file, 'r') as in_csv_fd:
                self.csv_reader = csv.reader(in_csv_fd, quoting=csv.QUOTE_NONE)
                self.fill_sequence(in_csv_fd, out_file)
        except IOError:
            print("Cannot find input file '%s'" % in_file)
            sys.exit(1)

    
    def fill_sequence(self, csv_reader, out_file):
        
        if out_file is None:
            out_fd = sys.stdout
        else:
            try:
                out_fd = open(out_file, 'w')
            except IOError:
                print("Could not open '%s' for writing" % out_file)
                sys.exit(1)
                
        try:
            # Copy header to output:
            out_fd.write(csv_reader.next())
            curr_second = 0
            curr_parent_state = None
            curr_child_state  = None
            curr_dyad_id      = None
            for one_line in csv_reader:
                data = one_line.strip().split()
                data = data[0].replace('"', "").split(',')
                dyad_id  = int(data[0])
                onset    = int(float(data[1]))
                parent   = data[2]
                child    = data[3]
                duration = data[4]
                if dyad_id != curr_dyad_id:
                    curr_parent_state = parent
                    curr_child_state  = child
                    curr_dyad_id      = dyad_id
                    curr_second       = 0
                if onset > curr_second:
                    # Fill the time gap with current states:
                    num_intermediate_secs = onset - curr_second
                    for sec in range(num_intermediate_secs):
                        self.write_tuple(out_fd, 
                                         dyad_id, 
                                         curr_second + sec, 
                                         curr_parent_state, 
                                         curr_child_state,
                                         duration)
                    
                    curr_second += num_intermediate_secs
                else:
                    curr_parent_state = parent
                    curr_child_state  = child
                    self.write_tuple(out_fd, dyad_id, curr_second, parent, child, duration)
                    curr_second += 1
                curr_parent_state = parent
                curr_child_state  = child
        finally:
            self.write_tuple(out_fd, dyad_id, curr_second, parent, child, duration)
            if out_fd != sys.stdout:
                out_fd.close()
                
    def write_tuple(self, out_fd, dyad_id, onset, parent, child, duration):        
        out_fd.write('%s,%s,%s,%s,%s\n' % (dyad_id,
                                        onset,
                                        parent,
                                        child,
                                        duration
                                        )
                    )
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-o', '--outFile',
                        help='fully qualified output file. Default: stdout \n',
                        dest='outFile',
                        default=None);
    parser.add_argument('inFile',
                        help='CSV file with data for state changes only.'
                        )

    args = parser.parse_args();

    StateSequenceRestorer(args.inFile, out_file=args.outFile)    
            