import ast
from typing import Optional

from pysource_codegen._codegen_rules import StdGenerator
from pysource_codegen._generator import Context
from pysource_codegen._generator import NodeRef
from pysource_codegen._utils import equal_ast


class _InvalidTree(Exception):
    pass


class AstChecker(StdGenerator):

    def check(self, tree: ast.AST, print=lambda *a: None) -> bool:
        self.target = tree
        try:
            new_tree = self.generate(type(tree).__name__)
        except (_InvalidTree, AttributeError, IndexError):
            return False
        return equal_ast(tree, new_tree, print)

    @property
    def rand(self):
        assert False

    def probability(self, parent_node, type_name, context) -> float:
        original = super().probability(parent_node, type_name, context)

        target_parent = parent_node.relocate(self.target)

        # If the target has None at this position, no concrete type can match.
        # This happens when a required field (qty='') has None in the target tree,
        # which is always an invalid AST (generate_UnionNodeType would silently
        # leave the field as None, causing a false-positive valid result).
        if target_parent.node is None:
            raise _InvalidTree()

        equal_current_type = type(target_parent.node).__name__ == type_name

        if equal_current_type and original <= 0:
            raise _InvalidTree()

        return 1 if equal_current_type else 0

    def attr_length_provider(self, parent_node: NodeRef):
        target_parent = parent_node.relocate(self.target)
        node_type = type(target_parent.node).__name__
        same_length = self.same_length()
        lengths: dict = {}

        def attr_length(attr_name, stop):
            if attr_name in lengths:
                return lengths[attr_name]
            # Enforce same_length: linked attrs must have the same count
            if node_type in same_length:
                attrs = same_length[node_type]
                if attr_name in attrs[1:]:
                    length = attr_length(attrs[0], stop)
                    lengths[attr_name] = length
                    return length
            length = len(getattr(target_parent.node, attr_name))
            if length < self.min_attr_length(node_type, attr_name):
                raise _InvalidTree()
            lengths[attr_name] = length
            return length

        return attr_length

    def _should_place_none(self, child_parent_node, quantity, new_node):
        if "?" not in quantity:
            return False
        target_is_none = child_parent_node.relocate(self.target).node is None
        # An optional field that the generator never fills with None (none_allowed=False)
        # should not be accepted as None in the target tree either.
        if target_is_none and not self.none_allowed(child_parent_node):
            raise _InvalidTree()
        return target_is_none

    def generate_BuiltinNodeType(
        self, place, parent_node, info, ast_type_name, depth, stop, context
    ):
        target_node = parent_node.relocate(self.target)
        place(target_node.node)

    def context_before(
        self, context: Context, node: NodeRef, attr: str, index: Optional[int]
    ) -> Context:
        ctx = super().context_before(context, node, attr, index)
        node_type = type(node.node).__name__
        # in_ann_assign_subscript_slice: the base StdGenerator conservatively sets
        # this flag whenever entering Subscript.slice inside AnnAssign.target,
        # because at generation time the AnnAssign.value hasn't been generated yet.
        # But the SyntaxError only fires when AnnAssign.value is None — when the
        # AnnAssign has a value, Starred in the subscript slice compiles fine.
        # The checker has access to the full target tree, so it can check here.
        if ctx.in_ann_assign_subscript_slice and (node_type, attr) == (
            "Subscript",
            "slice",
        ):
            target_subscript = node.relocate(self.target)
            if (
                target_subscript.parent is not None
                and isinstance(target_subscript.parent.node, ast.AnnAssign)
                and getattr(target_subscript.parent.node, "value", None) is not None
            ):
                ctx.in_ann_assign_subscript_slice = False
        return ctx
