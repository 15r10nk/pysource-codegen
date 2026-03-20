import ast

from pysource_codegen._codegen_rules import StdGenerator
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
