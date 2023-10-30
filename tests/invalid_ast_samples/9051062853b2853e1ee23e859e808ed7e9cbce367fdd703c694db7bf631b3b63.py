from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=JoinedStr(
                values=[
                    FormattedValue(
                        value=Name(id="name_0", ctx=Load()),
                        conversion=-1,
                        format_spec=JoinedStr(
                            values=[
                                FormattedValue(
                                    value=Name(id="name_1", ctx=Load()),
                                    conversion=115,
                                    format_spec=JoinedStr(
                                        values=[
                                            FormattedValue(
                                                value=Name(id="name_1", ctx=Load()),
                                                conversion=-1,
                                                format_spec=JoinedStr(
                                                    values=[
                                                        FormattedValue(
                                                            value=Name(
                                                                id="name_5", ctx=Load()
                                                            ),
                                                            conversion=97,
                                                        )
                                                    ]
                                                ),
                                            )
                                        ]
                                    ),
                                )
                            ]
                        ),
                    )
                ]
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# f'{name_0:{name_1!s:{name_1:{name_5!a}}}}'
#
#
# Error:
#     SyntaxError('f-string: expressions nested too deeply', ('<file>', 1, 28, "f'{name_0:{name_1!s:{name_1:{name_5!a}}}}'", 1, 28))
