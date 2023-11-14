async def test_lock():
    with something:

        def acquire_lock():
            return (yield from lock)
