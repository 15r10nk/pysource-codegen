def testNonlocal():
    x = 0

    def f():
        nonlocal x
        nonlocal x
