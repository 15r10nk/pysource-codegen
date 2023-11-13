def test_frame_resurrect():
    def gen():
        nonlocal frame

    del frame
