# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    AnnAssign(
      target=Subscript(
        value=IfExp(
          test=Lambda(
            args=arguments(
              vararg=arg(arg='name_4'),
              kwarg=arg(arg='name_0')),
            body=Name(id='name_0')),
          body=Call(
            func=Name(id='name_2'),
            args=[
              Name(id='name_4'),
              Name(id='name_4')],
            keywords=[
              keyword(
                value=Name(id='name_4')),
              keyword(
                arg='name_3',
                value=Name(id='name_3')),
              keyword(
                value=Name(id='name_2'))]),
          orelse=BinOp(
            left=Name(id='name_2'),
            op=FloorDiv(),
            right=Name(id='name_2'))),
        slice=Name(id='name_3'),
        ctx=Store()),
      annotation=TemplateStr(),
      value=JoinedStr(),
      simple=0),
    Expr(
      value=Call(
        func=UnaryOp(
          op=USub(),
          operand=UnaryOp(
            op=USub(),
            operand=Name(id='name_2'))),
        args=[
          DictComp(
            key=Lambda(
              args=arguments(),
              body=Name(id='name_0')),
            value=Subscript(
              value=Name(id='name_4'),
              slice=Name(id='name_1')),
            generators=[
              comprehension(
                target=Name(id='name_1', ctx=Store()),
                iter=JoinedStr(),
                ifs=[
                  Set(
                    elts=[
                      Name(id='name_0')]),
                  NamedExpr(
                    target=Name(id='name_3', ctx=Store()),
                    value=Name(id='name_5')),
                  JoinedStr(),
                  Constant(value=b''),
                  Call(
                    func=Name(id='name_5'))],
                is_async=0),
              comprehension(
                target=Subscript(
                  value=Name(id='name_1'),
                  slice=Name(id='name_0'),
                  ctx=Store()),
                iter=JoinedStr(),
                ifs=[
                  JoinedStr()],
                is_async=0)]),
          Name(id='name_1'),
          JoinedStr(
            values=[
              Constant(value='some const text'),
              FormattedValue(
                value=Name(id='name_4'),
                conversion=-1,
                format_spec=JoinedStr()),
              FormattedValue(
                value=Name(id='name_4'),
                conversion=-1,
                format_spec=JoinedStr()),
              Constant(value='b\'\\xfe\\xff\'\'"\'\'\'"""{}\\')]),
          Call(
            func=Set(
              elts=[
                Name(id='name_4'),
                Name(id='name_1')]),
            args=[
              Set(
                elts=[
                  Name(id='name_2'),
                  Name(id='name_0')]),
              NamedExpr(
                target=Name(id='name_5', ctx=Store()),
                value=Name(id='name_2')),
              Lambda(
                args=arguments(
                  vararg=arg(arg='name_1')),
                body=Name(id='name_2')),
              Lambda(
                args=arguments(),
                body=Name(id='name_1'))],
            keywords=[
              keyword(value=Dict())])],
        keywords=[
          keyword(
            value=Set(
              elts=[
                List(),
                SetComp(
                  elt=Name(id='name_0'),
                  generators=[
                    comprehension(
                      target=Name(id='name_4', ctx=Store()),
                      iter=Name(id='name_4'),
                      is_async=0)]),
                List(),
                Starred(
                  value=Name(id='name_1'))])),
          keyword(
            value=Compare(
              left=TemplateStr(),
              ops=[
                GtE(),
                NotIn()],
              comparators=[
                SetComp(
                  elt=Name(id='name_4'),
                  generators=[
                    comprehension(
                      target=Name(id='name_2', ctx=Store()),
                      iter=Name(id='name_3'),
                      is_async=0)]),
                Compare(
                  left=Name(id='name_4'),
                  ops=[
                    Gt()],
                  comparators=[
                    Name(id='name_1')])])),
          keyword(arg='name_3', value=Dict())])),
    For(
      target=Attribute(value=List(), attr='name_3', ctx=Store()),
      iter=DictComp(
        key=IfExp(
          test=TemplateStr(
            values=[
              Constant(value="Noneb'\\xfe\\xff' some const text")]),
          body=JoinedStr(
            values=[
              Constant(value="some const textb''False15")]),
          orelse=List(
            elts=[
              Name(id='name_2'),
              Name(id='name_3')])),
        value=DictComp(
          key=TemplateStr(
            values=[
              Constant(value='14True')]),
          generators=[
            comprehension(
              target=Name(id='name_2', ctx=Store()),
              iter=Attribute(
                value=Name(id='name_3'),
                attr='name_4'),
              ifs=[
                DictComp(
                  key=Name(id='name_3'),
                  value=Name(id='name_3'),
                  generators=[
                    comprehension(
                      target=Name(id='name_0', ctx=Store()),
                      iter=Name(id='name_2'),
                      is_async=0)])],
              is_async=0),
            comprehension(
              target=List(ctx=Store()),
              iter=SetComp(
                elt=Name(id='name_2'),
                generators=[
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0)]),
              ifs=[
                Subscript(
                  value=Name(id='name_4'),
                  slice=Name(id='name_5')),
                Call(
                  func=Name(id='name_0')),
                Compare(
                  left=Name(id='name_2'),
                  ops=[
                    NotIn()],
                  comparators=[
                    Name(id='name_1')]),
                Dict(),
                Set(
                  elts=[
                    Name(id='name_4')])],
              is_async=0),
            comprehension(
              target=Subscript(
                value=Name(id='name_4'),
                slice=Name(id='name_5'),
                ctx=Store()),
              iter=UnaryOp(
                op=Invert(),
                operand=Name(id='name_4')),
              ifs=[
                Call(
                  func=Name(id='name_3'))],
              is_async=0),
            comprehension(
              target=Attribute(
                value=Name(id='name_5'),
                attr='name_3',
                ctx=Store()),
              iter=IfExp(
                test=Name(id='name_3'),
                body=Name(id='name_2'),
                orelse=Name(id='name_1')),
              ifs=[
                Dict(),
                Name(id='name_0')],
              is_async=0),
            comprehension(
              target=Attribute(
                value=Name(id='name_4'),
                attr='name_4',
                ctx=Store()),
              iter=SetComp(
                elt=Name(id='name_5'),
                generators=[
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=0)]),
              ifs=[
                Constant(value=b'\xef\xbb\xbf'),
                SetComp(
                  elt=Name(id='name_5'),
                  generators=[
                    comprehension(
                      target=Name(id='name_3', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=0)]),
                Name(id='name_5'),
                Lambda(
                  args=arguments(
                    vararg=arg(arg='name_2'),
                    kwarg=arg(arg='name_4')),
                  body=Name(id='name_5')),
                BoolOp(
                  op=Or(),
                  values=[
                    Name(id='name_1'),
                    Name(id='name_2')])],
              is_async=0),
            comprehension(
              target=Attribute(
                value=Name(id='name_5'),
                attr='name_1',
                ctx=Store()),
              iter=DictComp(
                key=Name(id='name_3'),
                value=Name(id='name_5'),
                generators=[
                  comprehension(
                    target=Name(id='name_0', ctx=Store()),
                    iter=Name(id='name_5'),
                    is_async=0)]),
              is_async=0)]),
        generators=[
          comprehension(
            target=Tuple(
              elts=[
                Starred(
                  value=Name(id='name_2', ctx=Store()),
                  ctx=Store()),
                Attribute(
                  value=Name(id='name_2'),
                  attr='name_2',
                  ctx=Store()),
                Subscript(
                  value=Name(id='name_4'),
                  slice=Name(id='name_0'),
                  ctx=Store())],
              ctx=Store()),
            iter=BinOp(
              left=GeneratorExp(
                elt=Name(id='name_1'),
                generators=[
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=1)]),
              op=Mult(),
              right=Call(
                func=Name(id='name_2'))),
            is_async=0),
          comprehension(
            target=Subscript(
              value=Set(
                elts=[
                  Name(id='name_0')]),
              slice=Name(id='name_5'),
              ctx=Store()),
            iter=ListComp(
              elt=IfExp(
                test=Name(id='name_4'),
                body=Name(id='name_5'),
                orelse=Name(id='name_4')),
              generators=[
                comprehension(
                  target=Name(id='name_5', ctx=Store()),
                  iter=Name(id='name_2'),
                  ifs=[
                    Name(id='name_4'),
                    Name(id='name_3'),
                    Name(id='name_3'),
                    Name(id='name_4'),
                    Name(id='name_2')],
                  is_async=0)]),
            is_async=0),
          comprehension(
            target=Attribute(
              value=Lambda(
                args=arguments(),
                body=Name(id='name_1')),
              attr='name_3',
              ctx=Store()),
            iter=GeneratorExp(
              elt=Set(
                elts=[
                  Name(id='name_4')]),
              generators=[
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_4'),
                  ifs=[
                    Name(id='name_3'),
                    Name(id='name_3'),
                    Name(id='name_1'),
                    Name(id='name_3')],
                  is_async=1)]),
            is_async=0),
          comprehension(
            target=Attribute(
              value=GeneratorExp(
                elt=Name(id='name_1'),
                generators=[
                  comprehension(
                    target=Name(id='name_3', ctx=Store()),
                    iter=Name(id='name_0'),
                    is_async=1)]),
              attr='name_5',
              ctx=Store()),
            iter=Subscript(
              value=TemplateStr(),
              slice=IfExp(
                test=Name(id='name_3'),
                body=Name(id='name_5'),
                orelse=Name(id='name_0'))),
            is_async=0),
          comprehension(
            target=Subscript(
              value=List(),
              slice=ListComp(
                elt=Name(id='name_1'),
                generators=[
                  comprehension(
                    target=Name(id='name_3', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0)]),
              ctx=Store()),
            iter=UnaryOp(op=Not(), operand=List()),
            is_async=0),
          comprehension(
            target=Tuple(
              elts=[
                Attribute(
                  value=Name(id='name_0'),
                  attr='name_3',
                  ctx=Store()),
                Tuple(ctx=Store()),
                Attribute(
                  value=Name(id='name_4'),
                  attr='name_1',
                  ctx=Store()),
                Subscript(
                  value=Name(id='name_0'),
                  slice=Name(id='name_4'),
                  ctx=Store())],
              ctx=Store()),
            iter=Subscript(
              value=Set(
                elts=[
                  Name(id='name_0')]),
              slice=BoolOp(
                op=And(),
                values=[
                  Name(id='name_3'),
                  Name(id='name_4')])),
            ifs=[
              Tuple(
                elts=[
                  Attribute(
                    value=Name(id='name_3'),
                    attr='name_0'),
                  Constant(value=b'\'"\'\'\'"""{}\\'),
                  Constant(value='\'"\'\'\'"""{}\\')]),
              Compare(
                left=Constant(value=b'\'"\'\'\'"""{}\\'),
                ops=[
                  IsNot(),
                  Gt(),
                  Eq(),
                  In(),
                  Gt(),
                  GtE()],
                comparators=[
                  TemplateStr(),
                  Tuple(),
                  GeneratorExp(
                    elt=Name(id='name_0'),
                    generators=[
                      comprehension(
                        target=Name(id='name_0', ctx=Store()),
                        iter=Name(id='name_1'),
                        is_async=0)]),
                  Compare(
                    left=Name(id='name_1'),
                    ops=[
                      LtE()],
                    comparators=[
                      Name(id='name_1')]),
                  BoolOp(
                    op=Or(),
                    values=[
                      Name(id='name_3'),
                      Name(id='name_2')]),
                  JoinedStr()]),
              UnaryOp(op=Invert(), operand=Tuple()),
              JoinedStr()],
            is_async=0)]),
      body=[
        Expr(
          value=Compare(
            left=JoinedStr(
              values=[
                Constant(value=" b'some bytes'b'\\x00\\x00\\xfe\\xff'b'\\x00\\x00\\xfe\\xff'")]),
            ops=[
              Lt(),
              Eq(),
              NotEq()],
            comparators=[
              List(
                elts=[
                  Name(id='name_3')]),
              Dict(
                keys=[
                  None,
                  Name(id='name_5'),
                  Name(id='name_3'),
                  None,
                  None],
                values=[
                  Name(id='name_0'),
                  Name(id='name_1'),
                  Name(id='name_2'),
                  Name(id='name_3'),
                  Name(id='name_3')]),
              Subscript(
                value=Name(id='name_2'),
                slice=Name(id='name_0'))])),
        Expr(
          value=Constant(value=True)),
        Assign(
          targets=[
            Attribute(
              value=Attribute(
                value=Name(id='name_1'),
                attr='name_4'),
              attr='name_5',
              ctx=Store()),
            Tuple(
              elts=[
                Name(id='name_0', ctx=Store()),
                Tuple(
                  elts=[
                    Name(id='name_1', ctx=Store()),
                    Name(id='name_0', ctx=Store())],
                  ctx=Store()),
                Starred(
                  value=Name(id='name_2', ctx=Store()),
                  ctx=Store())],
              ctx=Store())],
          value=SetComp(
            elt=TemplateStr(),
            generators=[
              comprehension(
                target=List(ctx=Store()),
                iter=BoolOp(
                  op=And(),
                  values=[
                    Name(id='name_1'),
                    Name(id='name_5')]),
                ifs=[
                  Constant(value=b'\x00\x00\xfe\xff'),
                  BoolOp(
                    op=And(),
                    values=[
                      Name(id='name_2'),
                      Name(id='name_1')]),
                  Tuple(),
                  Set(
                    elts=[
                      Name(id='name_2')])],
                is_async=0),
              comprehension(
                target=Name(id='name_0', ctx=Store()),
                iter=Subscript(
                  value=Name(id='name_2'),
                  slice=Name(id='name_0')),
                ifs=[
                  Name(id='name_5'),
                  JoinedStr(),
                  Name(id='name_4'),
                  Compare(
                    left=Name(id='name_5'),
                    ops=[
                      IsNot()],
                    comparators=[
                      Name(id='name_5')])],
                is_async=0),
              comprehension(
                target=List(ctx=Store()),
                iter=Attribute(
                  value=Name(id='name_4'),
                  attr='name_4'),
                ifs=[
                  JoinedStr(),
                  Lambda(
                    args=arguments(
                      kwarg=arg(arg='name_4')),
                    body=Name(id='name_4')),
                  Call(
                    func=Name(id='name_2')),
                  IfExp(
                    test=Name(id='name_5'),
                    body=Name(id='name_1'),
                    orelse=Name(id='name_5')),
                  Set(
                    elts=[
                      Name(id='name_2')])],
                is_async=0),
              comprehension(
                target=Attribute(
                  value=Name(id='name_5'),
                  attr='name_5',
                  ctx=Store()),
                iter=Subscript(
                  value=Name(id='name_5'),
                  slice=Name(id='name_5')),
                ifs=[
                  Call(
                    func=Name(id='name_2')),
                  GeneratorExp(
                    elt=Name(id='name_2'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_2'),
                        is_async=1)]),
                  Call(
                    func=Name(id='name_1')),
                  Dict()],
                is_async=0),
              comprehension(
                target=Tuple(ctx=Store()),
                iter=Set(
                  elts=[
                    Name(id='name_4')]),
                ifs=[
                  Subscript(
                    value=Name(id='name_0'),
                    slice=Name(id='name_4')),
                  Attribute(
                    value=Name(id='name_1'),
                    attr='name_5'),
                  Call(
                    func=Name(id='name_5'))],
                is_async=0),
              comprehension(
                target=Subscript(
                  value=Name(id='name_0'),
                  slice=Name(id='name_3'),
                  ctx=Store()),
                iter=UnaryOp(
                  op=USub(),
                  operand=Name(id='name_1')),
                ifs=[
                  Constant(value='some const text', kind='u'),
                  Compare(
                    left=Name(id='name_3'),
                    ops=[
                      LtE()],
                    comparators=[
                      Name(id='name_4')]),
                  IfExp(
                    test=Name(id='name_2'),
                    body=Name(id='name_1'),
                    orelse=Name(id='name_1'))],
                is_async=0)])),
        Expr(
          value=SetComp(
            elt=IfExp(
              test=Name(id='name_5'),
              body=Name(id='name_0'),
              orelse=Name(id='name_1')),
            generators=[
              comprehension(
                target=Name(id='name_4', ctx=Store()),
                iter=Constant(value=True),
                ifs=[
                  DictComp(
                    key=Name(id='name_1'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_1'),
                        is_async=0)])],
                is_async=0)])),
        Expr(
          value=Tuple(
            elts=[
              Subscript(
                value=Name(id='name_1'),
                slice=Name(id='name_5')),
              Starred(
                value=Name(id='name_4'))]))],
      orelse=[
        Expr(
          value=SetComp(
            elt=DictComp(
              key=Name(id='name_5'),
              value=Name(id='name_2'),
              generators=[
                comprehension(
                  target=Name(id='name_1', ctx=Store()),
                  iter=Name(id='name_3'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_0'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_1', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_5', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0)]),
            generators=[
              comprehension(
                target=Name(id='name_0', ctx=Store()),
                iter=ListComp(
                  elt=Name(id='name_3'),
                  generators=[
                    comprehension(
                      target=Name(id='name_2', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=0)]),
                ifs=[
                  Compare(
                    left=Name(id='name_0'),
                    ops=[
                      Eq()],
                    comparators=[
                      Name(id='name_4')]),
                  UnaryOp(
                    op=Not(),
                    operand=Name(id='name_1'))],
                is_async=0),
              comprehension(
                target=Subscript(
                  value=Name(id='name_3'),
                  slice=Name(id='name_4'),
                  ctx=Store()),
                iter=SetComp(
                  elt=Name(id='name_4'),
                  generators=[
                    comprehension(
                      target=Name(id='name_0', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=0)]),
                ifs=[
                  Subscript(
                    value=Name(id='name_0'),
                    slice=Name(id='name_2')),
                  GeneratorExp(
                    elt=Name(id='name_3'),
                    generators=[
                      comprehension(
                        target=Name(id='name_1', ctx=Store()),
                        iter=Name(id='name_2'),
                        is_async=1)])],
                is_async=0)])),
        While(
          test=IfExp(
            test=DictComp(
              key=Name(id='name_1'),
              generators=[
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_3'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_1', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0)]),
            body=GeneratorExp(
              elt=Name(id='name_4'),
              generators=[
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0)]),
            orelse=UnaryOp(
              op=Not(),
              operand=Name(id='name_1'))),
          body=[
            Expr(
              value=TemplateStr(
                values=[
                  Constant(value='b\'\'b\'\\\'"\\\'\\\'\\\'"""{}\\\\\'\'"\'\'\'"""{}\\b\'some bytes\'b\'\\xff\\xfe\'')])),
            Expr(value=Dict()),
            Expr(value=TemplateStr()),
            Break(),
            Import(
              names=[
                alias(name='name_1', asname='name_4'),
                alias(name='name_1')],
              is_lazy=0)]),
        Expr(
          value=ListComp(
            elt=Name(id='name_3'),
            generators=[
              comprehension(
                target=Tuple(ctx=Store()),
                iter=GeneratorExp(
                  elt=Name(id='name_0'),
                  generators=[
                    comprehension(
                      target=Name(id='name_2', ctx=Store()),
                      iter=Name(id='name_1'),
                      is_async=0)]),
                is_async=0),
              comprehension(
                target=Subscript(
                  value=Name(id='name_5'),
                  slice=Name(id='name_1'),
                  ctx=Store()),
                iter=UnaryOp(
                  op=USub(),
                  operand=Name(id='name_3')),
                is_async=0),
              comprehension(
                target=Attribute(
                  value=Name(id='name_4'),
                  attr='name_1',
                  ctx=Store()),
                iter=BoolOp(
                  op=Or(),
                  values=[
                    Name(id='name_0'),
                    Name(id='name_2')]),
                ifs=[
                  ListComp(
                    elt=Name(id='name_1'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_5'),
                        is_async=0)]),
                  Tuple(),
                  Lambda(
                    args=arguments(
                      kwarg=arg(arg='name_2')),
                    body=Name(id='name_5'))],
                is_async=0),
              comprehension(
                target=Tuple(ctx=Store()),
                iter=UnaryOp(
                  op=USub(),
                  operand=Name(id='name_2')),
                ifs=[
                  Set(
                    elts=[
                      Name(id='name_1')]),
                  List(),
                  Subscript(
                    value=Name(id='name_0'),
                    slice=Name(id='name_1')),
                  Set(
                    elts=[
                      Name(id='name_4')]),
                  List()],
                is_async=0)]))]),
    Pass(),
    Expr(
      value=Name(id='name_5')),
    ClassDef(
      name='name_2',
      bases=[
        Tuple(
          elts=[
            Compare(
              left=Call(
                func=Name(id='name_4'),
                args=[
                  Name(id='name_2'),
                  Name(id='name_5'),
                  Name(id='name_0'),
                  Name(id='name_5'),
                  Name(id='name_0')],
                keywords=[
                  keyword(
                    arg='name_0',
                    value=Name(id='name_1'))]),
              ops=[
                In(),
                Is(),
                IsNot()],
              comparators=[
                Constant(value=b'\xef\xbb\xbf'),
                Compare(
                  left=Name(id='name_5'),
                  ops=[
                    Gt(),
                    NotIn(),
                    Lt(),
                    Gt(),
                    Gt()],
                  comparators=[
                    Name(id='name_3'),
                    Name(id='name_4'),
                    Name(id='name_5'),
                    Name(id='name_0'),
                    Name(id='name_4')]),
                Compare(
                  left=Name(id='name_3'),
                  ops=[
                    Eq(),
                    IsNot(),
                    Eq(),
                    NotIn(),
                    Lt()],
                  comparators=[
                    Name(id='name_0'),
                    Name(id='name_2'),
                    Name(id='name_1'),
                    Name(id='name_3'),
                    Name(id='name_5')])]),
            NamedExpr(
              target=Name(id='name_1', ctx=Store()),
              value=Compare(
                left=Name(id='name_0'),
                ops=[
                  Is(),
                  Lt()],
                comparators=[
                  Name(id='name_2'),
                  Name(id='name_3')])),
            TemplateStr(
              values=[
                Interpolation(
                  value=Name(id='name_5'),
                  str='name_5',
                  conversion=97),
                Constant(value='b\'\\\'"\\\'\\\'\\\'"""{}\\\\\'7.5200689139999755'),
                Interpolation(
                  value=Name(id='name_2'),
                  str='name_2',
                  conversion=97)]),
            Starred(
              value=Tuple(
                elts=[
                  Name(id='name_2'),
                  Name(id='name_1'),
                  Name(id='name_3'),
                  Name(id='name_5'),
                  Name(id='name_5')]))]),
        Starred(
          value=Attribute(
            value=BoolOp(
              op=Or(),
              values=[
                Name(id='name_3'),
                Name(id='name_4'),
                Name(id='name_0'),
                Name(id='name_0'),
                Name(id='name_0')]),
            attr='name_5')),
        Subscript(
          value=BinOp(
            left=Compare(
              left=Name(id='name_5'),
              ops=[
                Eq(),
                GtE(),
                GtE(),
                Lt()],
              comparators=[
                Name(id='name_1'),
                Name(id='name_4'),
                Name(id='name_5'),
                Name(id='name_0')]),
            op=Sub(),
            right=Constant(value=b'')),
          slice=Attribute(
            value=Subscript(
              value=Name(id='name_2'),
              slice=Name(id='name_1')),
            attr='name_1'))],
      keywords=[
        keyword(
          value=Set(
            elts=[
              UnaryOp(
                op=Invert(),
                operand=BinOp(
                  left=Name(id='name_4'),
                  op=RShift(),
                  right=Name(id='name_2')))])),
        keyword(
          arg='name_4',
          value=BoolOp(
            op=And(),
            values=[
              BoolOp(
                op=Or(),
                values=[
                  Attribute(
                    value=Name(id='name_5'),
                    attr='name_0'),
                  Subscript(
                    value=Name(id='name_4'),
                    slice=Name(id='name_4')),
                  BoolOp(
                    op=And(),
                    values=[
                      Name(id='name_4'),
                      Name(id='name_4')])]),
              ListComp(
                elt=List(),
                generators=[
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_4'),
                    ifs=[
                      Name(id='name_5'),
                      Name(id='name_2')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_3'),
                    ifs=[
                      Name(id='name_5')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_4'),
                    ifs=[
                      Name(id='name_3'),
                      Name(id='name_4'),
                      Name(id='name_5'),
                      Name(id='name_2'),
                      Name(id='name_3')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_2'),
                    ifs=[
                      Name(id='name_4')],
                    is_async=0)]),
              Call(
                func=Set(
                  elts=[
                    Name(id='name_5')]),
                args=[
                  IfExp(
                    test=Name(id='name_5'),
                    body=Name(id='name_1'),
                    orelse=Name(id='name_3')),
                  Call(
                    func=Name(id='name_4')),
                  Set(
                    elts=[
                      Name(id='name_5')]),
                  DictComp(
                    key=Name(id='name_4'),
                    value=Name(id='name_4'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_0'),
                        is_async=0)])],
                keywords=[
                  keyword(
                    arg='name_5',
                    value=Name(id='name_3'))])])),
        keyword(
          arg='name_0',
          value=Subscript(
            value=GeneratorExp(
              elt=UnaryOp(
                op=USub(),
                operand=Name(id='name_3')),
              generators=[
                comprehension(
                  target=Name(id='name_1', ctx=Store()),
                  iter=Name(id='name_5'),
                  ifs=[
                    Name(id='name_3')],
                  is_async=1),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_2'),
                  ifs=[
                    Name(id='name_1')],
                  is_async=0),
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_5'),
                  ifs=[
                    Name(id='name_5')],
                  is_async=1),
                comprehension(
                  target=Name(id='name_1', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_4'),
                  ifs=[
                    Name(id='name_2')],
                  is_async=1)]),
            slice=Lambda(
              args=arguments(
                posonlyargs=[
                  arg(arg='name_2')],
                args=[
                  arg(arg='name_5'),
                  arg(arg='name_0'),
                  arg(arg='name_3'),
                  arg(arg='name_1')]),
              body=SetComp(
                elt=Name(id='name_5'),
                generators=[
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0)])))),
        keyword(
          arg='name_3',
          value=TemplateStr(
            values=[
              Interpolation(
                value=Constant(value=6),
                str='6',
                conversion=97)]))],
      body=[
        Expr(
          value=Tuple(
            elts=[
              NamedExpr(
                target=Name(id='name_0', ctx=Store()),
                value=Name(id='name_2'))]))]),
    Expr(
      value=NamedExpr(
        target=Name(id='name_1', ctx=Store()),
        value=Call(
          func=Dict(
            keys=[
              Name(id='name_4'),
              None,
              Name(id='name_3'),
              Name(id='name_1')],
            values=[
              Name(id='name_3'),
              Name(id='name_5'),
              Name(id='name_1'),
              Name(id='name_3')]),
          args=[
            Tuple(
              elts=[
                Name(id='name_2'),
                Name(id='name_2'),
                Name(id='name_1'),
                Name(id='name_3'),
                Name(id='name_1')]),
            BoolOp(
              op=Or(),
              values=[
                Name(id='name_3'),
                Name(id='name_3'),
                Name(id='name_5'),
                Name(id='name_1'),
                Name(id='name_2'),
                Name(id='name_3'),
                Name(id='name_4')]),
            ListComp(
              elt=Name(id='name_5'),
              generators=[
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_3'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_2'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0)]),
            UnaryOp(
              op=Not(),
              operand=Name(id='name_5')),
            SetComp(
              elt=Name(id='name_5'),
              generators=[
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_2'),
                  is_async=0)])],
          keywords=[
            keyword(
              value=IfExp(
                test=Name(id='name_5'),
                body=Name(id='name_1'),
                orelse=Name(id='name_2'))),
            keyword(
              value=Set(
                elts=[
                  Name(id='name_2')])),
            keyword(
              arg='name_3',
              value=BinOp(
                left=Name(id='name_0'),
                op=Mult(),
                right=Name(id='name_2'))),
            keyword(
              value=Set(
                elts=[
                  Name(id='name_3')]))]))),
    Expr(
      value=Name(id='name_1')),
    Expr(
      value=Call(
        func=TemplateStr(
          values=[
            Interpolation(
              value=Name(id='name_3'),
              str='name_3',
              conversion=-1),
            Constant(value="Noneb''")]),
        args=[
          UnaryOp(
            op=Invert(),
            operand=UnaryOp(
              op=Invert(),
              operand=Name(id='name_1'))),
          Constant(value=True),
          UnaryOp(
            op=USub(),
            operand=BoolOp(
              op=And(),
              values=[
                Name(id='name_0'),
                Name(id='name_1'),
                Name(id='name_1'),
                Name(id='name_1'),
                Name(id='name_5'),
                Name(id='name_1')]))],
        keywords=[
          keyword(value=Dict())])),
    Delete(
      targets=[
        Subscript(
          value=Lambda(
            args=arguments(
              posonlyargs=[
                arg(arg='name_0'),
                arg(arg='name_4'),
                arg(arg='name_3'),
                arg(arg='name_5')],
              args=[
                arg(arg='name_1')],
              kwonlyargs=[
                arg(arg='name_2')],
              kw_defaults=[
                None],
              defaults=[
                Subscript(
                  value=Name(id='name_2'),
                  slice=Name(id='name_4')),
                Call(
                  func=Name(id='name_3'))]),
            body=BinOp(
              left=Name(id='name_1'),
              op=Div(),
              right=Name(id='name_4'))),
          slice=IfExp(
            test=BoolOp(
              op=Or(),
              values=[
                Name(id='name_3'),
                Name(id='name_2'),
                Name(id='name_2'),
                Name(id='name_1')]),
            body=ListComp(
              elt=Name(id='name_5'),
              generators=[
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_3'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_0'),
                  is_async=0)]),
            orelse=Constant(value=b'\'"\'\'\'"""{}\\')),
          ctx=Del()),
        Name(id='name_1', ctx=Del()),
        List(
          elts=[
            Tuple(
              elts=[
                List(
                  elts=[
                    Name(id='name_4', ctx=Del()),
                    Name(id='name_5', ctx=Del()),
                    Name(id='name_5', ctx=Del()),
                    Name(id='name_0', ctx=Del())],
                  ctx=Del()),
                Name(id='name_3', ctx=Del()),
                Tuple(ctx=Del()),
                List(ctx=Del())],
              ctx=Del()),
            Tuple(ctx=Del()),
            Name(id='name_0', ctx=Del()),
            Attribute(
              value=Constant(value=b''),
              attr='name_3',
              ctx=Del()),
            Attribute(
              value=IfExp(
                test=Name(id='name_1'),
                body=Name(id='name_5'),
                orelse=Name(id='name_0')),
              attr='name_3',
              ctx=Del())],
          ctx=Del())]),
    Expr(
      value=Call(
        func=Compare(
          left=BoolOp(
            op=Or(),
            values=[
              Name(id='name_3'),
              Name(id='name_3'),
              Name(id='name_2'),
              Name(id='name_4'),
              Name(id='name_4'),
              Name(id='name_0'),
              Name(id='name_5')]),
          ops=[
            In(),
            NotIn(),
            NotEq(),
            NotIn()],
          comparators=[
            DictComp(
              key=Name(id='name_5'),
              value=Name(id='name_1'),
              generators=[
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_4'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_0'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_2'),
                  is_async=0)]),
            DictComp(
              key=Name(id='name_0'),
              value=Name(id='name_3'),
              generators=[
                comprehension(
                  target=Name(id='name_4', ctx=Store()),
                  iter=Name(id='name_2'),
                  is_async=0)]),
            Constant(value='\'"\'\'\'"""{}\\'),
            BoolOp(
              op=Or(),
              values=[
                Name(id='name_4'),
                Name(id='name_0')])]),
        args=[
          DictComp(
            key=Subscript(
              value=Name(id='name_0'),
              slice=Name(id='name_3')),
            generators=[
              comprehension(
                target=Name(id='name_2', ctx=Store()),
                iter=Compare(
                  left=Name(id='name_2'),
                  ops=[
                    Eq()],
                  comparators=[
                    Name(id='name_5')]),
                ifs=[
                  Name(id='name_1')],
                is_async=0),
              comprehension(
                target=List(ctx=Store()),
                iter=Set(
                  elts=[
                    Name(id='name_0')]),
                ifs=[
                  Dict(),
                  GeneratorExp(
                    elt=Name(id='name_5'),
                    generators=[
                      comprehension(
                        target=Name(id='name_3', ctx=Store()),
                        iter=Name(id='name_1'),
                        is_async=1)]),
                  Name(id='name_2'),
                  Call(
                    func=Name(id='name_4'))],
                is_async=0)]),
          NamedExpr(
            target=Name(id='name_0', ctx=Store()),
            value=Tuple()),
          Lambda(
            args=arguments(
              posonlyargs=[
                arg(arg='name_1'),
                arg(arg='name_4')],
              args=[
                arg(arg='name_0'),
                arg(arg='name_3')],
              kwonlyargs=[
                arg(arg='name_5')],
              kw_defaults=[
                Attribute(
                  value=Name(id='name_0'),
                  attr='name_0')],
              defaults=[
                SetComp(
                  elt=Name(id='name_5'),
                  generators=[
                    comprehension(
                      target=Name(id='name_3', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=0)])]),
            body=Compare(
              left=Name(id='name_5'),
              ops=[
                NotEq()],
              comparators=[
                Name(id='name_1')]))],
        keywords=[
          keyword(
            arg='name_4',
            value=BinOp(
              left=Call(
                func=Name(id='name_1')),
              op=BitOr(),
              right=UnaryOp(
                op=Not(),
                operand=Name(id='name_4'))))])),
    Expr(
      value=SetComp(
        elt=IfExp(
          test=Dict(
            keys=[
              Name(id='name_4'),
              Name(id='name_1')],
            values=[
              Name(id='name_1'),
              Name(id='name_5')]),
          body=BinOp(
            left=Name(id='name_3'),
            op=Div(),
            right=Name(id='name_5')),
          orelse=Subscript(
            value=Name(id='name_1'),
            slice=Name(id='name_3'))),
        generators=[
          comprehension(
            target=Subscript(
              value=SetComp(
                elt=Name(id='name_0'),
                generators=[
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=0)]),
              slice=Constant(value=None),
              ctx=Store()),
            iter=SetComp(
              elt=DictComp(
                key=Name(id='name_3'),
                value=Name(id='name_5'),
                generators=[
                  comprehension(
                    target=Name(id='name_3', ctx=Store()),
                    iter=Name(id='name_5'),
                    is_async=0)]),
              generators=[
                comprehension(
                  target=Name(id='name_0', ctx=Store()),
                  iter=Name(id='name_1'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_2', ctx=Store()),
                  iter=Name(id='name_5'),
                  is_async=0),
                comprehension(
                  target=Name(id='name_3', ctx=Store()),
                  iter=Name(id='name_1'),
                  ifs=[
                    Name(id='name_0'),
                    Name(id='name_4'),
                    Name(id='name_3'),
                    Name(id='name_2')],
                  is_async=0)]),
            ifs=[
              Attribute(
                value=IfExp(
                  test=Name(id='name_3'),
                  body=Name(id='name_3'),
                  orelse=Name(id='name_3')),
                attr='name_0')],
            is_async=0),
          comprehension(
            target=List(ctx=Store()),
            iter=List(
              elts=[
                Starred(
                  value=Name(id='name_1'))]),
            ifs=[
              SetComp(
                elt=Dict(),
                generators=[
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_3'),
                    ifs=[
                      Name(id='name_2'),
                      Name(id='name_4'),
                      Name(id='name_5'),
                      Name(id='name_5')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_4'),
                    ifs=[
                      Name(id='name_3')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_0', ctx=Store()),
                    iter=Name(id='name_1'),
                    ifs=[
                      Name(id='name_3'),
                      Name(id='name_4')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_5'),
                    ifs=[
                      Name(id='name_0')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_0', ctx=Store()),
                    iter=Name(id='name_2'),
                    ifs=[
                      Name(id='name_5')],
                    is_async=0)]),
              Tuple(
                elts=[
                  JoinedStr()]),
              JoinedStr(
                values=[
                  FormattedValue(
                    value=Name(id='name_2'),
                    conversion=115,
                    format_spec=JoinedStr()),
                  FormattedValue(
                    value=Name(id='name_4'),
                    conversion=-1,
                    format_spec=JoinedStr()),
                  FormattedValue(
                    value=Name(id='name_1'),
                    conversion=-1,
                    format_spec=JoinedStr()),
                  FormattedValue(
                    value=Name(id='name_1'),
                    conversion=-1)]),
              ListComp(
                elt=IfExp(
                  test=Name(id='name_5'),
                  body=Name(id='name_2'),
                  orelse=Name(id='name_4')),
                generators=[
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_3'),
                    ifs=[
                      Name(id='name_2')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_5'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_1'),
                    ifs=[
                      Name(id='name_3'),
                      Name(id='name_1'),
                      Name(id='name_4')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_5'),
                    ifs=[
                      Name(id='name_3'),
                      Name(id='name_5'),
                      Name(id='name_0')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_4'),
                    ifs=[
                      Name(id='name_2'),
                      Name(id='name_5'),
                      Name(id='name_1')],
                    is_async=0)]),
              Name(id='name_0')],
            is_async=0),
          comprehension(
            target=Subscript(
              value=BoolOp(
                op=And(),
                values=[
                  Name(id='name_1'),
                  Name(id='name_0')]),
              slice=Name(id='name_2'),
              ctx=Store()),
            iter=List(
              elts=[
                Attribute(
                  value=Name(id='name_1'),
                  attr='name_1'),
                Dict()]),
            is_async=0),
          comprehension(
            target=Tuple(
              elts=[
                Starred(
                  value=Name(id='name_5', ctx=Store()),
                  ctx=Store()),
                Subscript(
                  value=Name(id='name_0'),
                  slice=Name(id='name_0'),
                  ctx=Store()),
                Name(id='name_1', ctx=Store()),
                Subscript(
                  value=Name(id='name_3'),
                  slice=Name(id='name_5'),
                  ctx=Store())],
              ctx=Store()),
            iter=Constant(value=b'\x00\x00\xfe\xff'),
            ifs=[
              JoinedStr(
                values=[
                  FormattedValue(
                    value=Name(id='name_0'),
                    conversion=115),
                  Constant(value="b'\\x00\\x00\\xfe\\xff'"),
                  FormattedValue(
                    value=Name(id='name_4'),
                    conversion=-1,
                    format_spec=JoinedStr()),
                  Constant(value='\'"\'\'\'"""{}\\b\'\\x00\\x00\\xfe\\xff\'')]),
              BinOp(
                left=Subscript(
                  value=Name(id='name_4'),
                  slice=Name(id='name_5')),
                op=FloorDiv(),
                right=Dict()),
              Tuple(
                elts=[
                  Constant(value=True),
                  Attribute(
                    value=Name(id='name_1'),
                    attr='name_3'),
                  List(),
                  IfExp(
                    test=Name(id='name_3'),
                    body=Name(id='name_1'),
                    orelse=Name(id='name_5'))]),
              Tuple(
                elts=[
                  ListComp(
                    elt=Name(id='name_1'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_0'),
                        is_async=0)])]),
              Lambda(
                args=arguments(
                  args=[
                    arg(arg='name_2')],
                  kwonlyargs=[
                    arg(arg='name_3'),
                    arg(arg='name_5')],
                  kw_defaults=[
                    None,
                    Name(id='name_4')]),
                body=Set(
                  elts=[
                    Name(id='name_1')]))],
            is_async=0),
          comprehension(
            target=Subscript(
              value=Name(id='name_3'),
              slice=Compare(
                left=Name(id='name_2'),
                ops=[
                  Gt()],
                comparators=[
                  Name(id='name_2')]),
              ctx=Store()),
            iter=Lambda(
              args=arguments(
                posonlyargs=[
                  arg(arg='name_4'),
                  arg(arg='name_5'),
                  arg(arg='name_3')],
                args=[
                  arg(arg='name_0')],
                defaults=[
                  Name(id='name_4')]),
              body=Yield(
                value=Name(id='name_1'))),
            is_async=0)])),
    Expr(
      value=TemplateStr(
        values=[
          Interpolation(
            value=JoinedStr(
              values=[
                Constant(value="16.7083359063436 b'\\xfe\\xff'b'\\xff\\xfe\\x00\\x00'b''")]),
            str="f'16.7083359063436 b\\'\\\\xfe\\\\xff\\'b\\'\\\\xff\\\\xfe\\\\x00\\\\x00\\'b\\'\\''",
            conversion=97,
            format_spec=JoinedStr(
              values=[
                Constant(value="b''b''b'\\xff\\xfe'")])),
          Interpolation(
            value=UnaryOp(
              op=Invert(),
              operand=Name(id='name_5')),
            str='~name_5',
            conversion=115),
          Constant(value="b'\\x00\\x00\\xfe\\xff'")])),
    Expr(
      value=Constant(value=None)),
    Expr(
      value=UnaryOp(
        op=USub(),
        operand=BoolOp(
          op=Or(),
          values=[
            NamedExpr(
              target=Name(id='name_3', ctx=Store()),
              value=Name(id='name_4')),
            TemplateStr(
              values=[
                Constant(value=' b\'\\xfe\\xff\'b\'\\x00\\x00\\xfe\\xff\'b\'some bytes\'b\'\\\'"\\\'\\\'\\\'"""{}\\\\\'')]),
            Constant(value=19.450400362878558),
            Set(
              elts=[
                Name(id='name_4'),
                Name(id='name_2'),
                Name(id='name_1'),
                Name(id='name_0'),
                Name(id='name_4'),
                Name(id='name_0')]),
            Set(
              elts=[
                Name(id='name_3'),
                Name(id='name_4'),
                Name(id='name_0')])]))),
    Match(
      subject=Compare(
        left=Name(id='name_0'),
        ops=[
          LtE(),
          NotEq(),
          Eq(),
          NotIn(),
          In()],
        comparators=[
          Attribute(
            value=List(
              elts=[
                Name(id='name_0')]),
            attr='name_1'),
          TemplateStr(
            values=[
              Constant(value="Noneb'\\xef\\xbb\\xbf'b'\\xef\\xbb\\xbf'")]),
          Attribute(
            value=BoolOp(
              op=And(),
              values=[
                Name(id='name_2'),
                Name(id='name_0'),
                Name(id='name_5'),
                Name(id='name_4'),
                Name(id='name_3'),
                Name(id='name_2'),
                Name(id='name_1')]),
            attr='name_0'),
          Lambda(
            args=arguments(
              posonlyargs=[
                arg(arg='name_2')],
              args=[
                arg(arg='name_5')],
              kwonlyargs=[
                arg(arg='name_4'),
                arg(arg='name_1'),
                arg(arg='name_3')],
              kw_defaults=[
                Tuple(),
                JoinedStr(),
                None]),
            body=Dict(
              keys=[
                None,
                Name(id='name_5'),
                Name(id='name_3'),
                None,
                Name(id='name_4')],
              values=[
                Name(id='name_1'),
                Name(id='name_1'),
                Name(id='name_5'),
                Name(id='name_1'),
                Name(id='name_0')])),
          Attribute(
            value=Lambda(
              args=arguments(
                kwarg=arg(arg='name_1')),
              body=Name(id='name_0')),
            attr='name_4')]),
      cases=[
        match_case(
          pattern=MatchClass(
            cls=Attribute(
              value=Attribute(
                value=Name(id='name_0'),
                attr='name_2'),
              attr='name_3'),
            patterns=[
              MatchSequence(
                patterns=[
                  MatchSequence(
                    patterns=[
                      MatchAs(
                        pattern=MatchAs(
                          pattern=MatchAs(
                            pattern=MatchAs(
                              pattern=MatchAs(name='name_0'),
                              name='name_1'),
                            name='name_2'),
                          name='name_4'),
                        name='name_5')])])]),
          guard=Lambda(
            args=arguments(
              posonlyargs=[
                arg(arg='name_4'),
                arg(arg='name_0'),
                arg(arg='name_5')],
              kwarg=arg(arg='name_1')),
            body=NamedExpr(
              target=Name(id='name_5', ctx=Store()),
              value=TemplateStr())),
          body=[
            Assign(
              targets=[
                Attribute(
                  value=Attribute(
                    value=Name(id='name_4'),
                    attr='name_4'),
                  attr='name_3',
                  ctx=Store()),
                Subscript(
                  value=Dict(),
                  slice=SetComp(
                    elt=Name(id='name_5'),
                    generators=[
                      comprehension(
                        target=Name(id='name_1', ctx=Store()),
                        iter=Name(id='name_4'),
                        is_async=0)]),
                  ctx=Store())],
              value=Lambda(
                args=arguments(
                  posonlyargs=[
                    arg(arg='name_5'),
                    arg(arg='name_1'),
                    arg(arg='name_4'),
                    arg(arg='name_0')],
                  defaults=[
                    Name(id='name_5')]),
                body=Call(
                  func=Name(id='name_1')))),
            Expr(
              value=JoinedStr(
                values=[
                  FormattedValue(
                    value=Name(id='name_3'),
                    conversion=97),
                  FormattedValue(
                    value=Name(id='name_0'),
                    conversion=114),
                  Constant(value='some const textFalse'),
                  FormattedValue(
                    value=Name(id='name_2'),
                    conversion=115)])),
            Assign(
              targets=[
                Attribute(
                  value=Subscript(
                    value=Name(id='name_3'),
                    slice=Name(id='name_3')),
                  attr='name_0',
                  ctx=Store())],
              value=Constant(value=19.117545045055788)),
            Expr(
              value=UnaryOp(
                op=Invert(),
                operand=ListComp(
                  elt=Name(id='name_3'),
                  generators=[
                    comprehension(
                      target=Name(id='name_1', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=0)]))),
            Expr(
              value=Tuple(
                elts=[
                  Lambda(
                    args=arguments(),
                    body=Name(id='name_0')),
                  GeneratorExp(
                    elt=Name(id='name_4'),
                    generators=[
                      comprehension(
                        target=Name(id='name_1', ctx=Store()),
                        iter=Name(id='name_3'),
                        is_async=0)]),
                  DictComp(
                    key=Name(id='name_4'),
                    generators=[
                      comprehension(
                        target=Name(id='name_4', ctx=Store()),
                        iter=Name(id='name_4'),
                        is_async=0)])]))]),
        match_case(
          pattern=MatchSequence(
            patterns=[
              MatchClass(
                cls=Attribute(
                  value=Name(id='name_5'),
                  attr='name_5'),
                patterns=[
                  MatchClass(
                    cls=Name(id='name_0'),
                    patterns=[
                      MatchAs(
                        pattern=MatchAs(name='name_3'),
                        name='name_4')])],
                kwd_attrs=[
                  'name_1',
                  'name_2',
                  'name_4',
                  'name_0'],
                kwd_patterns=[
                  MatchSingleton(value=True),
                  MatchValue(
                    value=Constant(value=b'\xfe\xff')),
                  MatchClass(
                    cls=Name(id='name_5')),
                  MatchSequence()])]),
          body=[
            Expr(
              value=GeneratorExp(
                elt=Lambda(
                  args=arguments(
                    vararg=arg(arg='name_3'),
                    kwarg=arg(arg='name_4')),
                  body=Name(id='name_2')),
                generators=[
                  comprehension(
                    target=Name(id='name_3', ctx=Store()),
                    iter=Name(id='name_1'),
                    ifs=[
                      Name(id='name_5')],
                    is_async=1),
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_4'),
                    ifs=[
                      Name(id='name_4'),
                      Name(id='name_0')],
                    is_async=1),
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_1'),
                    ifs=[
                      Name(id='name_0'),
                      Name(id='name_5'),
                      Name(id='name_3'),
                      Name(id='name_1')],
                    is_async=1),
                  comprehension(
                    target=Name(id='name_3', ctx=Store()),
                    iter=Name(id='name_3'),
                    ifs=[
                      Name(id='name_2'),
                      Name(id='name_4')],
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_0'),
                    ifs=[
                      Name(id='name_5'),
                      Name(id='name_4')],
                    is_async=1)])),
            For(
              target=Attribute(value=JoinedStr(), attr='name_0', ctx=Store()),
              iter=NamedExpr(
                target=Name(id='name_4', ctx=Store()),
                value=Subscript(
                  value=Name(id='name_4'),
                  slice=Name(id='name_2'))),
              body=[
                Expr(
                  value=IfExp(
                    test=Name(id='name_1'),
                    body=Name(id='name_3'),
                    orelse=Name(id='name_0'))),
                Expr(
                  value=Subscript(
                    value=Name(id='name_1'),
                    slice=Name(id='name_3'))),
                While(
                  test=IfExp(
                    test=Name(id='name_3'),
                    body=Name(id='name_4'),
                    orelse=Name(id='name_1')),
                  body=[
                    Expr(
                      value=Name(id='name_2')),
                    Raise(),
                    Expr(
                      value=Name(id='name_4')),
                    Expr(
                      value=Name(id='name_0'))],
                  orelse=[
                    Expr(
                      value=Name(id='name_5'))])],
              orelse=[
                Expr(value=Tuple())])]),
        match_case(
          pattern=MatchAs(name='name_4'),
          guard=Constant(value='\'"\'\'\'"""{}\\'),
          body=[
            Expr(
              value=BinOp(
                left=Name(id='name_5'),
                op=LShift(),
                right=NamedExpr(
                  target=Name(id='name_4', ctx=Store()),
                  value=Name(id='name_0')))),
            FunctionDef(
              name='name_2',
              args=arguments(
                posonlyargs=[
                  arg(arg='name_4')],
                args=[
                  arg(arg='name_1')],
                kwonlyargs=[
                  arg(arg='name_2'),
                  arg(arg='name_3')],
                kw_defaults=[
                  GeneratorExp(
                    elt=Name(id='name_5'),
                    generators=[
                      comprehension(
                        target=Name(id='name_3', ctx=Store()),
                        iter=Name(id='name_4'),
                        is_async=1)]),
                  None]),
              body=[
                Match(
                  subject=Set(
                    elts=[
                      Name(id='name_1')]),
                  cases=[
                    match_case(
                      pattern=MatchAs(
                        pattern=MatchAs(name='name_0'),
                        name='name_2'),
                      guard=Name(id='name_2'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass()]),
                    match_case(
                      pattern=MatchValue(
                        value=Constant(value=b'some bytes')),
                      guard=Name(id='name_0'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()]),
                    match_case(
                      pattern=MatchAs(name='name_2'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass()])]),
                TypeAlias(
                  name=Name(id='name_3', ctx=Store()),
                  type_params=[
                    ParamSpec(name='name_5'),
                    TypeVarTuple(name='name_0'),
                    ParamSpec(name='name_4'),
                    ParamSpec(
                      name='name_3',
                      default_value=Name(id='name_1'))],
                  value=BinOp(
                    left=Name(id='name_4'),
                    op=Mod(),
                    right=Name(id='name_1'))),
                For(
                  target=Subscript(
                    value=Name(id='name_4'),
                    slice=Name(id='name_4'),
                    ctx=Store()),
                  iter=BoolOp(
                    op=And(),
                    values=[
                      Name(id='name_1'),
                      Name(id='name_1')]),
                  body=[
                    Expr(
                      value=Name(id='name_0')),
                    Expr(
                      value=Name(id='name_4')),
                    Delete(
                      targets=[
                        Name(id='name_5', ctx=Del())]),
                    With(
                      items=[
                        withitem(
                          context_expr=Name(id='name_1'))],
                      body=[
                        Pass()]),
                    With(
                      items=[
                        withitem(
                          context_expr=Name(id='name_3'),
                          optional_vars=Name(id='name_4', ctx=Store()))],
                      body=[
                        Pass()])],
                  orelse=[
                    AsyncFunctionDef(
                      name='name_4',
                      args=arguments(
                        kwarg=arg(
                          arg='name_4',
                          annotation=Name(id='name_2'))),
                      body=[
                        Pass()]),
                    TypeAlias(
                      name=Name(id='name_3', ctx=Store()),
                      value=Name(id='name_4'))]),
                Expr(
                  value=Set(
                    elts=[
                      Name(id='name_5')])),
                Assign(
                  targets=[
                    Attribute(
                      value=Name(id='name_2'),
                      attr='name_1',
                      ctx=Store())],
                  value=ListComp(
                    elt=Name(id='name_5'),
                    generators=[
                      comprehension(
                        target=Name(id='name_1', ctx=Store()),
                        iter=Name(id='name_0'),
                        is_async=0)])),
                Expr(
                  value=ListComp(
                    elt=Name(id='name_4'),
                    generators=[
                      comprehension(
                        target=Name(id='name_2', ctx=Store()),
                        iter=Name(id='name_0'),
                        is_async=0)]))],
              decorator_list=[
                SetComp(
                  elt=Lambda(
                    args=arguments(),
                    body=Name(id='name_2')),
                  generators=[
                    comprehension(
                      target=Name(id='name_3', ctx=Store()),
                      iter=Name(id='name_0'),
                      ifs=[
                        Name(id='name_3'),
                        Name(id='name_2'),
                        Name(id='name_1'),
                        Name(id='name_0'),
                        Name(id='name_3')],
                      is_async=0),
                    comprehension(
                      target=Name(id='name_4', ctx=Store()),
                      iter=Name(id='name_1'),
                      ifs=[
                        Name(id='name_0')],
                      is_async=0),
                    comprehension(
                      target=Name(id='name_5', ctx=Store()),
                      iter=Name(id='name_4'),
                      ifs=[
                        Name(id='name_5')],
                      is_async=0),
                    comprehension(
                      target=Name(id='name_3', ctx=Store()),
                      iter=Name(id='name_3'),
                      ifs=[
                        Name(id='name_3')],
                      is_async=0),
                    comprehension(
                      target=Name(id='name_5', ctx=Store()),
                      iter=Name(id='name_1'),
                      ifs=[
                        Name(id='name_4')],
                      is_async=0)]),
                Compare(
                  left=Tuple(),
                  ops=[
                    GtE(),
                    NotEq()],
                  comparators=[
                    Compare(
                      left=Name(id='name_1'),
                      ops=[
                        LtE()],
                      comparators=[
                        Name(id='name_3')]),
                    Dict()]),
                Constant(value='\'"\'\'\'"""{}\\'),
                Set(
                  elts=[
                    UnaryOp(
                      op=USub(),
                      operand=Name(id='name_4')),
                    Compare(
                      left=Name(id='name_3'),
                      ops=[
                        GtE()],
                      comparators=[
                        Name(id='name_1')]),
                    Name(id='name_0')]),
                List(
                  elts=[
                    ListComp(
                      elt=Name(id='name_0'),
                      generators=[
                        comprehension(
                          target=Name(id='name_0', ctx=Store()),
                          iter=Name(id='name_1'),
                          is_async=0)]),
                    ListComp(
                      elt=Name(id='name_3'),
                      generators=[
                        comprehension(
                          target=Name(id='name_3', ctx=Store()),
                          iter=Name(id='name_1'),
                          is_async=0)]),
                    SetComp(
                      elt=Name(id='name_0'),
                      generators=[
                        comprehension(
                          target=Name(id='name_2', ctx=Store()),
                          iter=Name(id='name_3'),
                          is_async=0)])])],
              type_params=[
                TypeVar(name='name_3'),
                TypeVar(name='name_0')]),
            Pass(),
            TypeAlias(
              name=Name(id='name_1', ctx=Store()),
              type_params=[
                TypeVar(
                  name='name_0',
                  bound=IfExp(
                    test=Name(id='name_3'),
                    body=Name(id='name_4'),
                    orelse=Name(id='name_0'))),
                TypeVarTuple(name='name_5'),
                TypeVarTuple(name='name_2')],
              value=Constant(value=b'\xff\xfe\x00\x00'))]),
        match_case(
          pattern=MatchValue(
            value=Constant(value=b'\xff\xfe')),
          body=[
            Expr(
              value=Subscript(
                value=Lambda(
                  args=arguments(
                    kwarg=arg(arg='name_2')),
                  body=Name(id='name_1')),
                slice=Dict())),
            Pass()]),
        match_case(
          pattern=MatchAs(
            pattern=MatchMapping(
              keys=[
                Constant(value='')],
              patterns=[
                MatchMapping(
                  keys=[
                    Constant(value=b'\xef\xbb\xbf')],
                  patterns=[
                    MatchAs(
                      pattern=MatchAs(
                        pattern=MatchAs(
                          pattern=MatchAs(name='name_0'),
                          name='name_1'),
                        name='name_2'),
                      name='name_3')])]),
            name='name_5'),
          body=[
            Expr(
              value=Call(
                func=TemplateStr(),
                args=[
                  BoolOp(
                    op=Or(),
                    values=[
                      Name(id='name_2'),
                      Name(id='name_5')]),
                  List(),
                  BinOp(
                    left=Name(id='name_5'),
                    op=Pow(),
                    right=Name(id='name_1')),
                  IfExp(
                    test=Name(id='name_2'),
                    body=Name(id='name_3'),
                    orelse=Name(id='name_0'))],
                keywords=[
                  keyword(
                    value=Name(id='name_2')),
                  keyword(
                    arg='name_2',
                    value=Name(id='name_4')),
                  keyword(
                    arg='name_3',
                    value=Name(id='name_3'))])),
            While(
              test=SetComp(
                elt=Name(id='name_5'),
                generators=[
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_3'),
                    ifs=[
                      Name(id='name_3'),
                      Name(id='name_1'),
                      Name(id='name_1'),
                      Name(id='name_2'),
                      Name(id='name_1')],
                    is_async=0)]),
              body=[
                Expr(value=JoinedStr()),
                Expr(value=JoinedStr()),
                AugAssign(
                  target=Attribute(
                    value=Name(id='name_5'),
                    attr='name_1',
                    ctx=Store()),
                  op=Mult(),
                  value=Tuple()),
                FunctionDef(
                  name='name_1',
                  args=arguments(
                    args=[
                      arg(arg='name_3'),
                      arg(arg='name_5'),
                      arg(
                        arg='name_0',
                        annotation=Name(id='name_0')),
                      arg(
                        arg='name_2',
                        annotation=Name(id='name_2'))]),
                  body=[
                    Expr(
                      value=Name(id='name_3')),
                    Import(
                      names=[
                        alias(name='name_4')],
                      is_lazy=0),
                    Expr(
                      value=Name(id='name_1')),
                    Expr(
                      value=Name(id='name_5')),
                    Expr(
                      value=Name(id='name_4'))],
                  decorator_list=[
                    IfExp(
                      test=Name(id='name_5'),
                      body=Name(id='name_4'),
                      orelse=Name(id='name_4')),
                    ListComp(
                      elt=Name(id='name_0'),
                      generators=[
                        comprehension(
                          target=Name(id='name_2', ctx=Store()),
                          iter=Name(id='name_4'),
                          is_async=0)]),
                    Subscript(
                      value=Name(id='name_0'),
                      slice=Name(id='name_4')),
                    GeneratorExp(
                      elt=Name(id='name_4'),
                      generators=[
                        comprehension(
                          target=Name(id='name_5', ctx=Store()),
                          iter=Name(id='name_1'),
                          is_async=1)])],
                  returns=List(),
                  type_params=[
                    TypeVar(name='name_5'),
                    TypeVar(
                      name='name_2',
                      bound=Name(id='name_0')),
                    TypeVarTuple(name='name_0')])]),
            Match(
              subject=Constant(value=False),
              cases=[
                match_case(
                  pattern=MatchMapping(
                    keys=[
                      Constant(value=b'\xfe\xff')],
                    patterns=[
                      MatchAs(
                        pattern=MatchAs(name='name_2'),
                        name='name_4')]),
                  body=[
                    Expr(
                      value=Name(id='name_3')),
                    Raise(),
                    Expr(
                      value=Name(id='name_5')),
                    FunctionDef(
                      name='name_4',
                      args=arguments(),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()],
                      decorator_list=[
                        Name(id='name_4'),
                        Name(id='name_1'),
                        Name(id='name_2'),
                        Name(id='name_4'),
                        Name(id='name_4')],
                      type_params=[
                        TypeVar(
                          name='name_2',
                          bound=Name(id='name_4')),
                        TypeVar(
                          name='name_0',
                          bound=Name(id='name_5'),
                          default_value=Name(id='name_1'))]),
                    Import(
                      names=[
                        alias(name='name_5', asname='name_2'),
                        alias(name='name_0'),
                        alias(name='name_4')],
                      is_lazy=0),
                    If(
                      test=Name(id='name_4'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()])]),
                match_case(
                  pattern=MatchSingleton(value=None),
                  guard=Compare(
                    left=Name(id='name_5'),
                    ops=[
                      NotIn(),
                      In(),
                      GtE(),
                      Eq(),
                      GtE(),
                      Gt()],
                    comparators=[
                      Name(id='name_0'),
                      Name(id='name_5'),
                      Name(id='name_2'),
                      Name(id='name_1'),
                      Name(id='name_5'),
                      Name(id='name_5')]),
                  body=[
                    Expr(
                      value=Name(id='name_4')),
                    Expr(
                      value=Name(id='name_3')),
                    If(
                      test=Name(id='name_3'),
                      body=[
                        Pass()],
                      orelse=[
                        Pass()])]),
                match_case(
                  pattern=MatchAs(
                    pattern=MatchAs(name='name_0'),
                    name='name_2'),
                  guard=Compare(
                    left=Name(id='name_0'),
                    ops=[
                      IsNot(),
                      LtE()],
                    comparators=[
                      Name(id='name_1'),
                      Name(id='name_4')]),
                  body=[
                    While(
                      test=Name(id='name_3'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()]),
                    Expr(
                      value=Name(id='name_3')),
                    FunctionDef(
                      name='name_0',
                      args=arguments(
                        vararg=arg(
                          arg='name_4',
                          annotation=Name(id='name_2'))),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()],
                      decorator_list=[
                        Name(id='name_1'),
                        Name(id='name_2'),
                        Name(id='name_5'),
                        Name(id='name_0')],
                      type_params=[
                        ParamSpec(name='name_1'),
                        TypeVar(
                          name='name_3',
                          default_value=Name(id='name_2')),
                        ParamSpec(
                          name='name_5',
                          default_value=Name(id='name_0'))])]),
                match_case(
                  pattern=MatchAs(
                    pattern=MatchAs(name='name_0'),
                    name='name_2'),
                  body=[
                    For(
                      target=Name(id='name_1', ctx=Store()),
                      iter=Name(id='name_1'),
                      body=[
                        Pass(),
                        Pass(),
                        Pass(),
                        Pass()]),
                    Pass()])]),
            Expr(
              value=JoinedStr(
                values=[
                  FormattedValue(
                    value=Name(id='name_5'),
                    conversion=-1,
                    format_spec=JoinedStr()),
                  Constant(value="b'\\x00\\x00\\xfe\\xff'b'\\xff\\xfe'some const text")]))])]),
    Expr(
      value=Call(
        func=JoinedStr(
          values=[
            Constant(value="Noneb'\\x00\\x00\\xfe\\xff'")]),
        args=[
          Dict(
            keys=[
              DictComp(
                key=Name(id='name_0'),
                generators=[
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_0'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=0)])],
            values=[
              Compare(
                left=Name(id='name_1'),
                ops=[
                  In(),
                  Lt(),
                  LtE(),
                  In(),
                  LtE()],
                comparators=[
                  Name(id='name_2'),
                  Name(id='name_0'),
                  Name(id='name_2'),
                  Name(id='name_4'),
                  Name(id='name_3')])]),
          Compare(
            left=Call(
              func=Name(id='name_1'),
              args=[
                Name(id='name_1'),
                Name(id='name_3'),
                Name(id='name_4'),
                Name(id='name_4')]),
            ops=[
              Eq(),
              LtE(),
              NotEq(),
              LtE()],
            comparators=[
              DictComp(
                key=Name(id='name_4'),
                generators=[
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_1'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0)]),
              Subscript(
                value=Name(id='name_0'),
                slice=Name(id='name_3')),
              Constant(value=b'some bytes'),
              SetComp(
                elt=Name(id='name_1'),
                generators=[
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_0'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_5'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_2', ctx=Store()),
                    iter=Name(id='name_5'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_0', ctx=Store()),
                    iter=Name(id='name_3'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_1', ctx=Store()),
                    iter=Name(id='name_4'),
                    is_async=0)])]),
          Lambda(
            args=arguments(
              posonlyargs=[
                arg(arg='name_1'),
                arg(arg='name_0')],
              vararg=arg(arg='name_3'),
              kwonlyargs=[
                arg(arg='name_2'),
                arg(arg='name_4')],
              kw_defaults=[
                None,
                Set(
                  elts=[
                    Name(id='name_0')])]),
            body=Dict(
              keys=[
                Name(id='name_1'),
                Name(id='name_0'),
                None,
                Name(id='name_3'),
                Name(id='name_0')],
              values=[
                Name(id='name_0'),
                Name(id='name_0'),
                Name(id='name_4'),
                Name(id='name_2'),
                Name(id='name_2')])),
          Starred(
            value=IfExp(
              test=Name(id='name_2'),
              body=Name(id='name_5'),
              orelse=Name(id='name_3')))],
        keywords=[
          keyword(
            arg='name_5',
            value=BoolOp(
              op=And(),
              values=[
                Lambda(
                  args=arguments(),
                  body=Name(id='name_3')),
                Lambda(
                  args=arguments(),
                  body=Name(id='name_1')),
                UnaryOp(
                  op=Invert(),
                  operand=Name(id='name_2')),
                Lambda(
                  args=arguments(),
                  body=Name(id='name_1')),
                Constant(value=b''),
                DictComp(
                  key=Name(id='name_4'),
                  value=Name(id='name_1'),
                  generators=[
                    comprehension(
                      target=Name(id='name_5', ctx=Store()),
                      iter=Name(id='name_1'),
                      is_async=0)])])),
          keyword(
            arg='name_3',
            value=Subscript(
              value=UnaryOp(
                op=Invert(),
                operand=Name(id='name_5')),
              slice=Lambda(
                args=arguments(
                  vararg=arg(arg='name_4'),
                  kwarg=arg(arg='name_5')),
                body=Name(id='name_5')))),
          keyword(
            arg='name_2',
            value=JoinedStr(
              values=[
                FormattedValue(
                  value=Name(id='name_3'),
                  conversion=115),
                FormattedValue(
                  value=Name(id='name_5'),
                  conversion=97),
                FormattedValue(
                  value=Name(id='name_2'),
                  conversion=115),
                FormattedValue(
                  value=Name(id='name_4'),
                  conversion=115),
                Constant(value='True')])),
          keyword(
            value=Dict(
              keys=[
                ListComp(
                  elt=Name(id='name_5'),
                  generators=[
                    comprehension(
                      target=Name(id='name_5', ctx=Store()),
                      iter=Name(id='name_4'),
                      is_async=0)]),
                Attribute(
                  value=Name(id='name_4'),
                  attr='name_2'),
                None,
                BinOp(
                  left=Name(id='name_1'),
                  op=Mod(),
                  right=Name(id='name_3')),
                SetComp(
                  elt=Name(id='name_0'),
                  generators=[
                    comprehension(
                      target=Name(id='name_3', ctx=Store()),
                      iter=Name(id='name_0'),
                      is_async=0)])],
              values=[
                Call(
                  func=Name(id='name_3')),
                NamedExpr(
                  target=Name(id='name_4', ctx=Store()),
                  value=Name(id='name_5')),
                Constant(value=b'\'"\'\'\'"""{}\\'),
                JoinedStr(),
                Call(
                  func=Name(id='name_1'))]))])),
    Expr(
      value=SetComp(
        elt=NamedExpr(
          target=Name(id='name_1', ctx=Store()),
          value=SetComp(
            elt=Name(id='name_0'),
            generators=[
              comprehension(
                target=Name(id='name_0', ctx=Store()),
                iter=Name(id='name_4'),
                is_async=0),
              comprehension(
                target=Name(id='name_1', ctx=Store()),
                iter=Name(id='name_2'),
                is_async=0),
              comprehension(
                target=Name(id='name_1', ctx=Store()),
                iter=Name(id='name_1'),
                is_async=0),
              comprehension(
                target=Name(id='name_3', ctx=Store()),
                iter=Name(id='name_3'),
                is_async=0),
              comprehension(
                target=Name(id='name_5', ctx=Store()),
                iter=Name(id='name_2'),
                is_async=0),
              comprehension(
                target=Name(id='name_0', ctx=Store()),
                iter=Name(id='name_2'),
                is_async=0)])),
        generators=[
          comprehension(
            target=Attribute(
              value=UnaryOp(
                op=Not(),
                operand=Name(id='name_0')),
              attr='name_0',
              ctx=Store()),
            iter=Call(
              func=Tuple(),
              args=[
                ListComp(
                  elt=Name(id='name_4'),
                  generators=[
                    comprehension(
                      target=Name(id='name_4', ctx=Store()),
                      iter=Name(id='name_2'),
                      is_async=0)])],
              keywords=[
                keyword(
                  arg='name_2',
                  value=Name(id='name_3')),
                keyword(
                  value=Name(id='name_2'))]),
            ifs=[
              DictComp(
                key=Subscript(
                  value=Name(id='name_4'),
                  slice=Name(id='name_1')),
                value=GeneratorExp(
                  elt=Name(id='name_5'),
                  generators=[
                    comprehension(
                      target=Name(id='name_1', ctx=Store()),
                      iter=Name(id='name_5'),
                      is_async=1)]),
                generators=[
                  comprehension(
                    target=Name(id='name_4', ctx=Store()),
                    iter=Name(id='name_2'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_5', ctx=Store()),
                    iter=Name(id='name_0'),
                    is_async=0),
                  comprehension(
                    target=Name(id='name_0', ctx=Store()),
                    iter=Name(id='name_1'),
                    ifs=[
                      Name(id='name_0')],
                    is_async=0)]),
              JoinedStr(
                values=[
                  FormattedValue(
                    value=Name(id='name_4'),
                    conversion=-1,
                    format_spec=JoinedStr()),
                  FormattedValue(
                    value=Name(id='name_3'),
                    conversion=115)]),
              BoolOp(
                op=Or(),
                values=[
                  NamedExpr(
                    target=Name(id='name_1', ctx=Store()),
                    value=Name(id='name_2')),
                  Name(id='name_3'),
                  Name(id='name_2'),
                  DictComp(
                    key=Name(id='name_5'),
                    generators=[
                      comprehension(
                        target=Name(id='name_2', ctx=Store()),
                        iter=Name(id='name_3'),
                        is_async=0)]),
                  Tuple(),
                  Call(
                    func=Name(id='name_4')),
                  Dict()])],
            is_async=0)])),
    Expr(
      value=Set(
        elts=[
          UnaryOp(
            op=Not(),
            operand=Attribute(
              value=Name(id='name_0'),
              attr='name_1')),
          Name(id='name_3')])),
    Import(
      names=[
        alias(name='name_3', asname='name_0'),
        alias(name='name_5'),
        alias(name='name_0'),
        alias(name='name_3', asname='name_0')],
      is_lazy=1)],
  type_ignores=[
    TypeIgnore(lineno=3, tag=''),
    TypeIgnore(lineno=5, tag=''),
    TypeIgnore(lineno=5, tag='some text'),
    TypeIgnore(lineno=5, tag=''),
    TypeIgnore(lineno=4, tag=''),
    TypeIgnore(lineno=0, tag=''),
    TypeIgnore(lineno=2, tag='some text'),
    TypeIgnore(lineno=4, tag=''),
    TypeIgnore(lineno=0, tag=''),
    TypeIgnore(lineno=4, tag='some text'),
    TypeIgnore(lineno=5, tag=''),
    TypeIgnore(lineno=3, tag=''),
    TypeIgnore(lineno=5, tag='some text'),
    TypeIgnore(lineno=5, tag=''),
    TypeIgnore(lineno=1, tag='some text'),
    TypeIgnore(lineno=0, tag='some text'),
    TypeIgnore(lineno=3, tag='some text'),
    TypeIgnore(lineno=1, tag=''),
    TypeIgnore(lineno=3, tag='some text'),
    TypeIgnore(lineno=4, tag='')])

# version: 3.15.0rc2+dev
# seed = 1368993664
#
# tree.body[12].value.values[0].value.values[0].value: "16.7083359063436 b'\\xfe\\xff'b'\\xff\\xfe\\x00\\x00'b''" != '16.7083359063436 b_\\xfe\\xff_b_\\xff\\xfe\\x00\\x00_b__'Source:
# ((name_2(name_4, name_4, **name_4, name_3=name_3, **name_2) if (lambda *name_4, **name_0: name_0) else name_2 // name_2)[name_3]): t'' = f''
# (--name_2)({lambda: name_0: name_4[name_1] for name_1 in f'' if {name_0} if (name_3 := name_5) if f'' if b'' if name_5() for name_1[name_0] in f'' if f''}, name_1, f'some const text{name_4:}{name_4:}b\'\\xfe\\xff\'\'"\'\'\'"""{{}}\\', {name_4, name_1}({name_2, name_0}, (name_5 := name_2), lambda *name_1: name_2, lambda: name_1, **{}), **{[], {name_0 for name_4 in name_4}, [], *name_1}, **(t'' >= {name_4 for name_2 in name_3} not in (name_4 > name_1)), name_3={})
# for [].name_3 in {f'some const textb\'\'False15' if t'Noneb\'\\xfe\\xff\' some const text' else [name_2, name_3]: {**t'14True' for name_2 in name_3.name_4 if {name_3: name_3 for name_0 in name_2} for [] in {name_2 for name_5 in name_3} if name_4[name_5] if name_0() if name_2 not in name_1 if {} if {name_4} for name_4[name_5] in ~name_4 if name_3() for name_5.name_3 in (name_2 if name_3 else name_1) if {} if name_0 for name_4.name_4 in {name_5 for name_5 in name_2} if b'\xef\xbb\xbf' if {name_5 for name_3 in name_5} if name_5 if (lambda *name_2, **name_4: name_5) if name_1 or name_2 for name_5.name_1 in {name_3: name_5 for name_0 in name_5}} for *name_2, name_2.name_2, name_4[name_0] in (name_1 async for name_4 in name_2) * name_2() for {name_0}[name_5] in [name_5 if name_4 else name_4 for name_5 in name_2 if name_4 if name_3 if name_3 if name_4 if name_2] for (lambda: name_1).name_3 in ({name_4} async for name_2 in name_4 if name_3 if name_3 if name_1 if name_3) for (name_1 async for name_3 in name_0).name_5 in t''[(name_5 if name_3 else name_0)] for [][[name_1 for name_3 in name_3]] in not [] for name_0.name_3, (), name_4.name_1, name_0[name_4] in {name_0}[(name_3 and name_4)] if (name_3.name_0, b'\'"\'\'\'"""{}\\', '\'"\'\'\'"""{}\\') if b'\'"\'\'\'"""{}\\' is not t'' > () == (name_0 for name_0 in name_1) in (name_1 <= name_1) > (name_3 or name_2) >= f'' if ~() if f''}:
#     f' b\'some bytes\'b\'\\x00\\x00\\xfe\\xff\'b\'\\x00\\x00\\xfe\\xff\'' < [name_3] == {**name_0, name_5: name_1, name_3: name_2, **name_3, **name_3} != name_2[name_0]
#     True
#     name_1.name_4.name_5 = name_0, (name_1, name_0), *name_2 = {t'' for [] in name_1 and name_5 if b'\x00\x00\xfe\xff' if name_2 and name_1 if () if {name_2} for name_0 in name_2[name_0] if name_5 if f'' if name_4 if name_5 is not name_5 for [] in name_4.name_4 if f'' if (lambda **name_4: name_4) if name_2() if (name_1 if name_5 else name_5) if {name_2} for name_5.name_5 in name_5[name_5] if name_2() if (name_2 async for name_4 in name_2) if name_1() if {} for () in {name_4} if name_0[name_4] if name_1.name_5 if name_5() for name_0[name_3] in -name_1 if u'some const text' if name_3 <= name_4 if (name_1 if name_2 else name_1)}
#     {name_0 if name_5 else name_1 for name_4 in True if {**name_1 for name_4 in name_1}}
#     name_1[name_5], *name_4
# else:
#     {{name_5: name_2 for name_1 in name_3 for name_2 in name_5 for name_3 in name_0 for name_1 in name_4 for name_5 in name_1} for name_0 in [name_3 for name_2 in name_5] if name_0 == name_4 if not name_1 for name_3[name_4] in {name_4 for name_0 in name_5} if name_0[name_2] if (name_3 async for name_1 in name_2)}
#     while (name_4 for name_3 in name_5) if {**name_1 for name_0 in name_3 for name_1 in name_4 for name_3 in name_5 for name_2 in name_4 for name_2 in name_5} else not name_1:
#         t'b\'\'b\'\\\'"\\\'\\\'\\\'"""{{}}\\\\\'\'"\'\'\'"""{{}}\\b\'some bytes\'b\'\\xff\\xfe\''
#         {}
#         t''
#         break
#         import name_1 as name_4, name_1
#     [name_3 for () in (name_0 for name_2 in name_1) for name_5[name_1] in -name_3 for name_4.name_1 in name_0 or name_2 if [name_1 for name_4 in name_5] if () if (lambda **name_2: name_5) for () in -name_2 if {name_1} if [] if name_0[name_1] if {name_4} if []]
# pass
# name_5
#
#
# class name_2((name_4(name_2, name_5, name_0, name_5, name_0, name_0=name_1) in b'\xef\xbb\xbf' is (name_5 > name_3 not in name_4 < name_5 > name_0 > name_4) is not (name_3 == name_0 is not name_2 == name_1 not in name_3 < name_5), (name_1 := name_0 is name_2 < name_3), t'{name_5!a}b\'\\\'"\\\'\\\'\\\'"""{{}}\\\\\'7.5200689139999755{name_2!a}', *((name_2, name_1, name_3, name_5, name_5))), *(name_3 or name_4 or name_0 or name_0 or name_0).name_5, ((name_5 == name_1 >= name_4 >= name_5 < name_0) - b'')[name_2[name_1].name_1], **{~(name_4 >> name_2)}, name_4=(name_5.name_0 or name_4[name_4] or name_4 and name_4) and [[] for name_2 in name_4 if name_5 if name_2 for name_5 in name_3 if name_5 for name_4 in name_4 if name_3 if name_4 if name_5 if name_2 if name_3 for name_4 in name_2 if name_4] and {name_5}(name_1 if name_5 else name_3, name_4(), {name_5}, {name_4: name_4 for name_4 in name_0}, name_5=name_3), name_0=(-name_3 async for name_1 in name_5 if name_3 for name_2 in name_5 for name_2 in name_2 if name_1 async for name_4 in name_5 if name_5 for name_1 in name_1 async for name_4 in name_4 if name_2)[(lambda name_2, /, name_5, name_0, name_3, name_1: {name_5 for name_4 in name_3})], name_3=t'{6!a}'):
#     (name_0 := name_2),
# (name_1 := {name_4: name_3, **name_5, name_3: name_1, name_1: name_3}((name_2, name_2, name_1, name_3, name_1), name_3 or name_3 or name_5 or name_1 or name_2 or name_3 or name_4, [name_5 for name_0 in name_1 for name_4 in name_4 for name_0 in name_3 for name_0 in name_2 for name_4 in name_1], not name_5, {name_5 for name_3 in name_2}, **(name_1 if name_5 else name_2), **{name_2}, name_3=name_0 * name_2, **{name_3}))
# name_1
# t'{name_3}Noneb\'\''(~~name_1, True, -(name_0 and name_1 and name_1 and name_1 and name_5 and name_1), **{})
# del (lambda name_0, name_4, name_3, name_5=name_2[name_4], /, name_1=name_3(), *, name_2: name_1 / name_4)[([name_5 for name_0 in name_3 for name_3 in name_4 for name_2 in name_0] if name_3 or name_2 or name_2 or name_1 else b'\'"\'\'\'"""{}\\')], name_1, [([name_4, name_5, name_5, name_0], name_3, (), []), (), name_0, b''.name_3, (name_5 if name_1 else name_0).name_3]
# ((name_3 or name_3 or name_2 or name_4 or name_4 or name_0 or name_5) in {name_5: name_1 for name_3 in name_4 for name_4 in name_0 for name_3 in name_1 for name_0 in name_2} not in {name_0: name_3 for name_4 in name_2} != '\'"\'\'\'"""{}\\' not in (name_4 or name_0))({**name_0[name_3] for name_2 in name_2 == name_5 if name_1 for [] in {name_0} if {} if (name_5 async for name_3 in name_1) if name_2 if name_4()}, (name_0 := ()), lambda name_1, name_4, /, name_0, name_3={name_5 for name_3 in name_5}, *, name_5=name_0.name_0: name_5 != name_1, name_4=name_1() | (not name_4))
# {name_3 / name_5 if {name_4: name_1, name_1: name_5} else name_1[name_3] for {name_0 for name_4 in name_2}[None] in {{name_3: name_5 for name_3 in name_5} for name_0 in name_1 for name_2 in name_5 for name_3 in name_1 if name_0 if name_4 if name_3 if name_2} if (name_3 if name_3 else name_3).name_0 for [] in [*name_1] if {{} for name_1 in name_2 for name_1 in name_3 if name_2 if name_4 if name_5 if name_5 for name_5 in name_4 if name_3 for name_0 in name_1 if name_3 if name_4 for name_4 in name_5 if name_0 for name_0 in name_2 if name_5} if (f'',) if f'{name_2!s:}{name_4:}{name_1:}{name_1}' if [name_2 if name_5 else name_4 for name_5 in name_3 if name_2 for name_1 in name_5 for name_4 in name_1 if name_3 if name_1 if name_4 for name_4 in name_5 if name_3 if name_5 if name_0 for name_4 in name_4 if name_2 if name_5 if name_1] if name_0 for (name_1 and name_0)[name_2] in [name_1.name_1, {}] for *name_5, name_0[name_0], name_1, name_3[name_5] in b'\x00\x00\xfe\xff' if f'{name_0!s}b\'\\x00\\x00\\xfe\\xff\'{name_4:}\'"\'\'\'"""{{}}\\b\'\\x00\\x00\\xfe\\xff\'' if name_4[name_5] // {} if (True, name_1.name_3, [], name_1 if name_3 else name_5) if ([name_1 for name_4 in name_0],) if (lambda name_2, *, name_3, name_5=name_4: {name_1}) for name_3[(name_2 > name_2)] in (lambda name_4, name_5, name_3, /, name_0=name_4: (yield name_1))}
# t'{f'16.7083359063436 b\'\\xfe\\xff\'b\'\\xff\\xfe\\x00\\x00\'b\'\''!a:b\'\'b\'\'b\'\\xff\\xfe\'}{~name_5!s}b\'\\x00\\x00\\xfe\\xff\''
# None
# -((name_3 := name_4) or t' b\'\\xfe\\xff\'b\'\\x00\\x00\\xfe\\xff\'b\'some bytes\'b\'\\\'"\\\'\\\'\\\'"""{{}}\\\\\'' or 19.450400362878558 or {name_4, name_2, name_1, name_0, name_4, name_0} or {name_3, name_4, name_0})
# match name_0 <= [name_0].name_1 != t'Noneb\'\\xef\\xbb\\xbf\'b\'\\xef\\xbb\\xbf\'' == (name_2 and name_0 and name_5 and name_4 and name_3 and name_2 and name_1).name_0 not in (lambda name_2, /, name_5, *, name_4=(), name_1=f'', name_3: {**name_1, name_5: name_1, name_3: name_5, **name_1, name_4: name_0}) in (lambda **name_1: name_0).name_4:
#     case name_0.name_2.name_3([[(((name_0 as name_1) as name_2) as name_4) as name_5]]) if lambda name_4, name_0, name_5, /, **name_1: (name_5 := t''):
#         name_4.name_4.name_3 = {}[{name_5 for name_1 in name_4}] = lambda name_5, name_1, name_4, name_0=name_5, /: name_1()
#         f'{name_3!a}{name_0!r}some const textFalse{name_2!s}'
#         name_3[name_3].name_0 = 19.117545045055788
#         ~[name_3 for name_1 in name_5]
#         lambda: name_0, (name_4 for name_1 in name_3), {**name_4 for name_4 in name_4}
#     case [name_5.name_5(name_0(name_3 as name_4), name_1=True, name_2=b'\xfe\xff', name_4=name_5(), name_0=[])]:
#         (lambda *name_3, **name_4: name_2 async for name_3 in name_1 if name_5 async for name_5 in name_4 if name_4 if name_0 async for name_2 in name_1 if name_0 if name_5 if name_3 if name_1 for name_3 in name_3 if name_2 if name_4 async for name_4 in name_0 if name_5 if name_4)
#         for f''.name_0 in (name_4 := name_4[name_2]):
#             name_3 if name_1 else name_0
#             name_1[name_3]
#             while name_4 if name_3 else name_1:
#                 name_2
#                 raise
#                 name_4
#                 name_0
#             else:
#                 name_5
#         else:
#             ()
#     case name_4 if '\'"\'\'\'"""{}\\':
#         name_5 << (name_4 := name_0)
#
#         @{lambda: name_2 for name_3 in name_0 if name_3 if name_2 if name_1 if name_0 if name_3 for name_4 in name_1 if name_0 for name_5 in name_4 if name_5 for name_3 in name_3 if name_3 for name_5 in name_1 if name_4}
#         @() >= (name_1 <= name_3) != {}
#         @'\'"\'\'\'"""{}\\'
#         @{-name_4, name_3 >= name_1, name_0}
#         @[[name_0 for name_0 in name_1], [name_3 for name_3 in name_1], {name_0 for name_2 in name_3}]
#         def name_2[name_3, name_0](name_4, /, name_1, *, name_2=(name_5 async for name_3 in name_4), name_3):
#             match {name_1}:
#                 case name_0 as name_2 if name_2:
#                     pass
#                     pass
#                     pass
#                 case b'some bytes' if name_0:
#                     pass
#                     pass
#                     pass
#                     pass
#                     pass
#                 case name_2:
#                     pass
#                     pass
#                     pass
#             type name_3[**name_5, *name_0, **name_4, **name_3 = name_1] = name_4 % name_1
#             for name_4[name_4] in name_1 and name_1:
#                 name_0
#                 name_4
#                 del name_5
#                 with name_1:
#                     pass
#                 with name_3 as name_4:
#                     pass
#             else:
#
#                 async def name_4(**name_4: name_2):
#                     pass
#                 type name_3 = name_4
#             {name_5}
#             name_2.name_1 = [name_5 for name_1 in name_0]
#             [name_4 for name_2 in name_0]
#         pass
#         type name_1[name_0: name_4 if name_3 else name_0, *name_5, *name_2] = b'\xff\xfe\x00\x00'
#     case b'\xff\xfe':
#         (lambda **name_2: name_1)[{}]
#         pass
#     case {'': {b'\xef\xbb\xbf': ((name_0 as name_1) as name_2) as name_3}} as name_5:
#         t''(name_2 or name_5, [], name_5 ** name_1, name_3 if name_2 else name_0, **name_2, name_2=name_4, name_3=name_3)
#         while {name_5 for name_5 in name_3 if name_3 if name_1 if name_1 if name_2 if name_1}:
#             f''
#             f''
#             name_5.name_1 *= ()
#
#             @name_4 if name_5 else name_4
#             @[name_0 for name_2 in name_4]
#             @name_0[name_4]
#             @(name_4 async for name_5 in name_1)
#             def name_1[name_5, name_2: name_0, *name_0](name_3, name_5, name_0: name_0, name_2: name_2) -> []:
#                 name_3
#                 import name_4
#                 name_1
#                 name_5
#                 name_4
#         match False:
#             case {b'\xfe\xff': name_2 as name_4}:
#                 name_3
#                 raise
#                 name_5
#
#                 @name_4
#                 @name_1
#                 @name_2
#                 @name_4
#                 @name_4
#                 def name_4[name_2: name_4, name_0: name_5 = name_1]():
#                     pass
#                     pass
#                     pass
#                     pass
#                     pass
#                 import name_5 as name_2, name_0, name_4
#                 if name_4:
#                     pass
#                     pass
#                     pass
#                     pass
#                     pass
#             case None if name_5 not in name_0 in name_5 >= name_2 == name_1 >= name_5 > name_5:
#                 name_4
#                 name_3
#                 if name_3:
#                     pass
#                 else:
#                     pass
#             case name_0 as name_2 if name_0 is not name_1 <= name_4:
#                 while name_3:
#                     pass
#                     pass
#                     pass
#                     pass
#                 name_3
#
#                 @name_1
#                 @name_2
#                 @name_5
#                 @name_0
#                 def name_0[**name_1, name_3 = name_2, **name_5 = name_0](*name_4: name_2):
#                     pass
#                     pass
#                     pass
#                     pass
#             case name_0 as name_2:
#                 for name_1 in name_1:
#                     pass
#                     pass
#                     pass
#                     pass
#                 pass
#         f'{name_5:}b\'\\x00\\x00\\xfe\\xff\'b\'\\xff\\xfe\'some const text'
# f'Noneb\'\\x00\\x00\\xfe\\xff\''({{**name_0 for name_2 in name_0 for name_2 in name_2}: name_1 in name_2 < name_0 <= name_2 in name_4 <= name_3}, name_1(name_1, name_3, name_4, name_4) == {**name_4 for name_1 in name_1 for name_2 in name_3} <= name_0[name_3] != b'some bytes' <= {name_1 for name_5 in name_3 for name_1 in name_0 for name_4 in name_5 for name_2 in name_5 for name_0 in name_3 for name_1 in name_4}, lambda name_1, name_0, /, *name_3, name_2, name_4={name_0}: {name_1: name_0, name_0: name_0, **name_4, name_3: name_2, name_0: name_2}, *(name_5 if name_2 else name_3), name_5=(lambda: name_3) and (lambda: name_1) and ~name_2 and (lambda: name_1) and b'' and {name_4: name_1 for name_5 in name_1}, name_3=(~name_5)[(lambda *name_4, **name_5: name_5)], name_2=f'{name_3!s}{name_5!a}{name_2!s}{name_4!s}True', **{[name_5 for name_5 in name_4]: name_3(), name_4.name_2: (name_4 := name_5), **b'\'"\'\'\'"""{}\\', name_1 % name_3: f'', {name_0 for name_3 in name_0}: name_1()})
# {(name_1 := {name_0 for name_0 in name_4 for name_1 in name_2 for name_1 in name_1 for name_3 in name_3 for name_5 in name_2 for name_0 in name_2}) for (not name_0).name_0 in ()([name_4 for name_4 in name_2], name_2=name_3, **name_2) if {name_4[name_1]: (name_5 async for name_1 in name_5) for name_4 in name_2 for name_5 in name_0 for name_0 in name_1 if name_0} if f'{name_4:}{name_3!s}' if (name_1 := name_2) or name_3 or name_2 or {**name_5 for name_2 in name_3} or () or name_4() or {}}
# {not name_0.name_1, name_3}
# lazy import name_3 as name_0, name_5, name_0, name_3 as name_0
#
#
