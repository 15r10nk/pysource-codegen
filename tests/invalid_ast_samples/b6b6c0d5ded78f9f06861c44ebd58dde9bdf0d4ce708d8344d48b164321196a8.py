from ast import *

tree = Module(
    body=[
        Delete(
            targets=[
                Subscript(
                    value=Name(id="name_2", ctx=Load()),
                    slice=Index(
                        value=Subscript(
                            value=Name(id="name_0", ctx=Load()),
                            slice=ExtSlice(
                                dims=[
                                    ExtSlice(
                                        dims=[
                                            ExtSlice(
                                                dims=[
                                                    ExtSlice(
                                                        dims=[
                                                            Index(
                                                                value=Name(
                                                                    id="name_2",
                                                                    ctx=Load(),
                                                                )
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            ctx=Load(),
                        )
                    ),
                    ctx=Del(),
                )
            ]
        )
    ],
    type_ignores=[],
)

# version: 3.8.16
# seed = 8040275
#
# Source:
#
# del name_2[name_0[name_2]]
#
#
#
# Error:
#     SystemError('extended slice invalid in nested slice')
