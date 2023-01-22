import flake8

import os
import abc


class X:

    @abc.abstractmethod
    def x():
        pass


def main():
    print("cwd", os.getcwd())
    print("flake8", flake8.__version__)


if __name__ == "__main__":
    main()
