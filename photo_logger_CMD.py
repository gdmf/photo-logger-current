import datetime
import collections
import json
import sys
from photologger.data import Data

print "\nPlease wait while the application loads modules..."

import arcpy


def run(config_file):

    with open(config_file, 'r') as src:
        data = json.load(src, object_pairs_hook=collections.OrderedDict)
    print "Start: {}\n".format(datetime.datetime.now())

    d = Data(data)
    d.process()
    print "\nEnd: {}\n".format(datetime.datetime.now())

if __name__ == '__main__':
    config_file = sys.argv[1]
    run(config_file)
