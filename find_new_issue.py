from random import randint

from tests.test_invalid_ast import generate_invalid_ast

if __name__ == "__main__":
    while True:
        i = randint(0, 10000000000)
        if generate_invalid_ast(i):
            break
        # TODO: search later for more valid source codes
        # if generate_valid_source(i):
        #    break
