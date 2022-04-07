import sys
from team import Team


def main():
    name = sys.argv[1]
    team = Team(name)
    team.start()


if __name__ == '__main__':
    main()
