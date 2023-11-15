import argparse
from ArcheReader import ArcheReader

# parse arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-t', '--test', default=False, action='store_true')
parser.add_argument('-s', '--save-frames', default=False, action='store_true')
parser.add_argument('-d', '--debug', default=False, action='store_true')
parser.add_argument('-k', '--kiosk', default=False, action='store_true')
parser.add_argument('-f', '--flask', default=False, action='store_true')
parser.add_argument('-p', '--parameters', default=False, action='store_true')

args = parser.parse_args()

archeReader = None
  
if __name__ == "__main__":
  archeReader = ArcheReader(args)
  # archeReader.run()