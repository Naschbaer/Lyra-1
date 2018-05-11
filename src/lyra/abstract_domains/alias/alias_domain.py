"""
Syntactic Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies.
A program variable can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Caterina Urban and Simon Wehrli
"""

from copy import deepcopy
from typing import List, Dict, Type

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.abstract_domains.alias.alias_lattice import AliasLattice
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing
from lyra.core.types import IntegerLyraType, BooleanLyraType, ListLyraType, NdarrayLyraType
from lyra.core.utils import copy_docstring

from lyra.core.expressions import *




class AliasStore(Store):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. document private methods
    .. automethod:: AliasStore._less_equal
    .. automethod:: AliasStore._meet
    .. automethod:: AliasStore._join
    """
    def __init__(self, variables: List[VariableIdentifier], lattices: Dict[Type, Type[Lattice]]):
        """Map each program variable to its usage status.

        :param variables: list of program variables
        :param lattices: dictionary from variable types to the corresponding lattice types
        """
        super().__init__(variables, lattices)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    def increase(self) -> 'AliasStore':
        """Increase the nesting level.

        :return: current lattice element modified to reflect an increased nesting level

        The increase is performed point-wise for each variable.
        """
#        for var in self.store:
#            self.store[var].increase()
        return self

    def decrease(self, other: 'AliasStore') -> 'AliasStore':
        """Decrease the nesting level by combining lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to reflect a decreased nesting level

        The decrease is performed point-wise for each variable.
        """
#        for var in self.store:
#            self.store[var].decrease(other.store[var])
        return self


class SimpleAliasStore(AliasStore):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: SimpleAliasStore._less_equal
    .. automethod:: SimpleAliasStore._meet
    .. automethod:: SimpleAliasStore._join
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to its usage status.

        :param variables: list of program variables
        """
        types = [BooleanLyraType, IntegerLyraType, ListLyraType, NdarrayLyraType]
        lattices = {typ: AliasLattice for typ in types}
        super().__init__(variables, lattices)


class SimpleAliasState(Stack, State):
    """Input data usage analysis state.
    An element of the syntactic usage abstract domain.

    Stack of maps from each program variable to its usage status.
    The stack contains a single map by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: UsageState._assign
    .. automethod:: UsageState._assume
    .. automethod:: UsageState._output
    .. automethod:: UsageState._substitute
    """
    def __init__(self, variables: List[VariableIdentifier]):
        super().__init__(SimpleAliasStore, {'variables': variables})

    @copy_docstring(Stack.push)
    def push(self):
        if self.is_bottom() or self.is_top():
            return self
        self.stack.append(deepcopy(self.lattice).increase())
        return self

    @copy_docstring(Stack.pop)
    def pop(self):
        if self.is_bottom() or self.is_top():
            return self
        current = self.stack.pop()
        self.lattice.decrease(current)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
#        raise RuntimeError("Unexpected assignment in a backward analysis!")
        if isinstance(left, VariableIdentifier):
            if isinstance(left.typ, (NdarrayLyraType, ListLyraType)):
                evaluation = self._evaluation.visit(right, self, dict())
                self.lattice.store[left] = evaluation[right]
            elif isinstance(left.typ, (IntegerLyraType, BooleanLyraType)):
                self.lattice.store[left] = AliasLattice()
            else:
                raise ValueError(f"Variable type {left.typ} is not supported!")
        else:
            raise NotImplementedError(f"Assignment to {left.__class__.__name__} is not supported!")
        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'SimpleAliasState':
        effect = False      # effect of the current nesting level on the outcome of the program
#        for variable in self.lattice.variables:
#            value = self.lattice.store[variable]
#            if value.is_written() or value.is_top():
#                effect = True
#        if effect:      # the current nesting level has an effect on the outcome of the program
#            for identifier in condition.ids():
#                if isinstance(identifier, VariableIdentifier):
#                    self.lattice.store[identifier].top()
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'SimpleAliasState':
        return self.push()

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'SimpleAliasState':
        return self.pop()

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'SimpleAliasState':
        return self.push()

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'SimpleAliasState':
        return self.pop()

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'SimpleAliasState':
        for identifier in output.ids():
            if isinstance(identifier, VariableIdentifier):
                self.lattice.store[identifier].top()
        return self

    @copy_docstring(State.raise_error)
    def raise_error(self):
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'SimpleAliasState':
        if isinstance(left, VariableIdentifier):
            if self.lattice.store[left].is_top() or self.lattice.store[left].is_scoped():
                # the assigned variable is used or scoped
                self.lattice.store[left].written()
                for identifier in right.ids():
                    if isinstance(identifier, VariableIdentifier):
                        self.lattice.store[identifier].top()
                    else:
                        error = f"Substitution with {right} is not implemented!"
                        raise NotImplementedError(error)
            return self
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            target = left.target
            if self.lattice.store[target].is_top() or self.lattice.store[target].is_scoped():
                # the assigned variable is used or scoped
                self.lattice.store[target].top()      # summarization abstraction
                for identifier in right.ids():
                    if isinstance(identifier, VariableIdentifier):
                        self.lattice.store[identifier].top()
                    else:
                        error = f"Substitution with {right} is not implemented!"
                        raise NotImplementedError(error)
            return self
        error = f"Substitution for {left} is not yet implemented!"
        raise NotImplementedError(error)
       
        
        
        
        
        
        
        
    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == "True":
                    evaluation[expr] = IntervalLattice(1, 1)
                else:  # expr.val == "False":
                    evaluation[expr] = IntervalLattice(0, 0)
                return evaluation
            elif isinstance(expr.typ, IntegerLyraType):
                val = int(expr.val)
                evaluation[expr] = IntervalLattice(val, val)
                return evaluation
            elif isinstance(expr.typ, FloatLyraType):
                val = float(expr.val)
                evaluation[expr] = IntervalLattice(val, val)
                return evaluation
            raise ValueError(f"Literal type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                evaluation[expr] = IntervalLattice(0, 1)
                return evaluation
            elif isinstance(expr.typ, IntegerLyraType) or isinstance(expr.typ, FloatLyraType):
                evaluation[expr] = IntervalLattice()
                return evaluation
            raise ValueError(f"Input type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType) or isinstance(expr.typ, IntegerLyraType)\
                    or isinstance(expr.typ, FloatLyraType):
                evaluation[expr] = deepcopy(state.store[expr])
                return evaluation
            raise ValueError(f"Variable type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            evaluation[expr] = AliasLattice().allocate()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                evaluated[expr] = deepcopy(evaluated[expr.expression]).neg()
                return evaluated
            raise ValueError(f"Unary operator '{expr.operator}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(expr.expression.typ, BooleanLyraType):
                    value = evaluated[expr.expression]
                    if value == IntervalLattice(0, 1):
                        evaluated[expr] = IntervalLattice(0, 1)
                        return evaluated
                    elif value == IntervalLattice(1, 1):
                        evaluated[expr] = IntervalLattice(0, 0)
                        return evaluated
                    elif value == IntervalLattice(0, 0):
                        evaluated[expr] = IntervalLattice(1, 1)
                        return evaluated
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).add(evaluated2[expr.right])
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).sub(evaluated2[expr.right])
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).mult(evaluated2[expr.right])
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()    # static class member shared between all instances