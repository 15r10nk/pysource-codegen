from pysource_codegen._generator import NodeRef


class RulesBase:

    def is_valid_AST(self, parent_node: NodeRef, node_name: str, context): ...
