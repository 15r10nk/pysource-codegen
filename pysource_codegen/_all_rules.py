import importlib
import inspect
import pkgutil
from pathlib import Path

from pysource_codegen._generator import NodeRef
from pysource_codegen.rules.rules_base import RulesBase


class AllRules:
    def __init__(self):
        self.rules = []
        rules_pkg = "pysource_codegen.rules"
        rules_path = Path(__file__).parent / "rules"
        for _, module_name, is_pkg in pkgutil.iter_modules([str(rules_path)]):
            if is_pkg:
                continue
            mod = importlib.import_module(f"{rules_pkg}.{module_name}")
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, RulesBase) and obj is not RulesBase:
                    self.rules.append(obj())

    def is_valid(self, parent: NodeRef, type_name, context):
        """
        checks if the given type_name is a valid ast node type as a child of the given parent in the given context
        """
        # Call all is_valid_AST methods in the rules
        for rule in self.rules:
            parent_type_name = type(parent.node).__name__

            for method_name in (
                f"is_valid_{parent_type_name}_{parent.parent_attr}",
                "is_valid",
            ):

                try:
                    method = getattr(rule, method_name)
                except AttributeError:
                    pass
                else:
                    method(parent, type_name, context)

    def fix(self, node):
        for rule in self.rules:
            node = rule.fix(node)
        return node

    def fix_result(self, node):
        for rule in self.rules:
            node = rule.fix_result(node)
        return node


all_rules = AllRules()
