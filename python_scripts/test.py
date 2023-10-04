import argparse
parser = argparse.ArgumentParser(description="hi test")
parser.add_argument("x",help="none given")

args = parser.parse_args()
print(args)
print(args.x)