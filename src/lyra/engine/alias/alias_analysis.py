"""
Input Data Usage Analysis
=========================

:Author: Caterina Urban
"""

from lyra.abstract_domains.alias.alias_domain import SimpleAliasState
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics


class AliasAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return SimpleAliasState(self.variables)
