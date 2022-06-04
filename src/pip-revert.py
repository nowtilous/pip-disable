import sys
from pip._internal.operations.freeze import freeze


def main(*args):
    print(args)
    for lib in freeze():
        print(lib)

if __name__ == "__main__":
    main(sys.argv)
