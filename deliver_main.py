import sys
from deliver import Deliver


def main():
    goods_names = sys.argv[2:]
    name = sys.argv[1]
    deliver = Deliver(name, goods_names)
    deliver.start()


if __name__ == '__main__':
    main()
