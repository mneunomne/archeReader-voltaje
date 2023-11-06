import argparse
from ArcheReader import ArcheReader
# from socket_connection import connectSocket

# parse arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-t', '--test', default=False, action='store_true')
args = parser.parse_args()

# check if test mode
test = args.test 

# capture element
global capture

capture = None
  
if __name__ == "__main__":
  archeReader = ArcheReader(test)
  archeReader.run()