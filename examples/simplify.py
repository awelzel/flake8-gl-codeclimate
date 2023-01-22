import os


def main():
    try:
        os.unlink("/dev/null/dev/null")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
