"""
Assumption Lattice
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from enum import IntEnum, Enum

from copy import deepcopy

from lyra.abstract_domains.lattice import Lattice, BottomMixin, BoundedLattice
from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType
from lyra.core.utils import copy_docstring


class TypeLattice(BottomMixin):
    """Type Lattice::

        Any
         |
        Float
         |
        Int
         |
        Bool

    The default lattice element is ``Any``.

    .. document private methods
    .. automethod:: TypeLattice._less_equal
    .. automethod:: TypeLattice._meet
    .. automethod:: TypeLattice._join
    .. automethod:: TypeLattice._widening
    """

    class Status(IntEnum):
        """Type status.

        The current lattice element can be:

        * ``Any``: Used as top element for any type

        * ``Float``: Float type

        * ``Int`` Integer type

        * ``Bool`` Boolean type
        """
        Any = 3
        Float = 2
        Int = 1
        Bool = 0

    def __init__(self, type_status: Status = Status.Any):
        super().__init__()
        self._element = type_status

    @classmethod
    def from_lyra_type(cls, lyra_type: LyraType):
        if isinstance(lyra_type, BooleanLyraType):
            return cls(TypeLattice.Status.Bool)
        elif isinstance(lyra_type, IntegerLyraType):
            return cls(TypeLattice.Status.Int)
        elif isinstance(lyra_type, FloatLyraType):
            return cls(TypeLattice.Status.Float)
        return cls(TypeLattice.Status.Any)

    @property
    def element(self) -> Status:
        if self.is_bottom():
            return None
        return self._element

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return self.element.name

    @copy_docstring(Lattice.top)
    def top(self) -> 'TypeLattice':
        self.replace(TypeLattice(TypeLattice.Status.Any))
        return self

    def real(self) -> 'TypeLattice':
        """Float lattice element.

        :return: current lattice element modified to be the Float lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Float))
        return self

    def integer(self) -> 'TypeLattice':
        """Int lattice element.

        :return: current lattice element modified to be the Int lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Int))
        return self

    def boolean(self) -> 'TypeLattice':
        """Bool lattice element.

        :return: current lattice element modified to be the Bool lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Bool))
        return self

    def is_real(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type float
        """
        return self.element == TypeLattice.Status.Float

    def is_integer(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type int
        """
        return self.element == TypeLattice.Status.Int

    def is_boolean(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type bool
        """
        return self.element == TypeLattice.Status.Bool

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.element == TypeLattice.Status.Any

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'TypeLattice') -> bool:
        return self.element <= other.element

    @copy_docstring(Lattice._join)
    def _join(self, other: 'TypeLattice') -> 'TypeLattice':
        self.replace(TypeLattice(max(self.element, other.element)))
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'TypeLattice') -> 'TypeLattice':
        self.replace(TypeLattice(min(self.element, other.element)))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'TypeLattice') -> 'TypeLattice':
        return self._join(other)


class AssumptionLattice(Lattice):
    """
    The Assumption Lattice is represented as a dictionary with different kinds of assumptions.
    The 'type_assmp' element is an assumption of the type.
    The 'range_assmp' element is an assumption about the range.

    The default element is the tuple with all assumption elements set to top.

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    class Assumption(Enum):
        """
        Name of the assumptions that are covered by the assumption lattice

        * ``type_assmp``: Used for assumptions about the type

        * ``range_assmp``: Used for assumptions about the range of values
        """

        type_assmp = 'type_assmp'
        range_assmp = 'range_assmp'

    def __init__(self, type_element=None, range_element=None):
        super().__init__()
        if type_element is None:
            type_element = TypeLattice().top()
        if range_element is None:
            range_element = IntervalLattice().top()
        self._assumptions = {
            AssumptionLattice.Assumption.type_assmp: type_element,
            AssumptionLattice.Assumption.range_assmp: range_element
        }
        self.pp = None

    def __repr__(self):
        assumptions = [self.type_assumption, self.range_assumption]
        assumption_repr = [assumption.__repr__() for assumption in assumptions]
        comma_separated = ', '.join(assumption_repr)
        return f'({comma_separated})'

    @property
    def assumptions(self):
        return self._assumptions

    @property
    def type_assumption(self):
        return self.assumptions[AssumptionLattice.Assumption.type_assmp]

    @property
    def range_assumption(self):
        return self.assumptions[AssumptionLattice.Assumption.range_assmp]

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        for assumption in self.assumptions.values():
            assumption.bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        for assumption in self.assumptions.values():
            assumption.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        for assumption in self.assumptions.values():
            if assumption.is_bottom():
                return True
        return False

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        for assumption in self.assumptions.values():
            if not assumption.is_top():
                return False
        return True

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'AssumptionLattice') -> bool:
        return self.type_assumption.less_equal(other.type_assumption) \
               and self.range_assumption.less_equal(other.range_assumption)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.join(other.type_assumption)
        self.range_assumption.join(other.range_assumption)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.meet(other.type_assumption)
        self.range_assumption.meet(other.range_assumption)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.widening(other.type_assumption)
        self.range_assumption.widening(other.range_assumption)
        return self


class InputAssumptionLattice(BoundedLattice):
    """
    The Input Assumption Lattice consists of two elements:
    iterations: the number of times the same assumption applies
    assumptions: the assumption for those inputs

    The default element is the element with 1 iteration and an empty list.

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    def __init__(self, iterations=1, assmps=None, pp=None):
        super().__init__()
        self.iterations = iterations
        self._assmps = assmps if assmps is not None else []
        self.is_loop = False
        self.join_as_loop = False
        self.condition = None
        self.pp = pp
        self.infoloss = False
        self.is_main = False

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        if self.is_top():
            return "T"
        if self.iterations == 1:
            return self.assmps.__repr__()
        return f"{self.iterations} x {self.assmps.__repr__()}"

    @property
    def assmps(self):
        if self.is_bottom() or self.is_top():
            return None
        return self._assmps

    def add_assumption_front(self, assmp: AssumptionLattice):
        """Adds an assumption to the front of the assumption list.

        :param assmp: assumption to be added to the list of current assumptions
        """
        self._assmps.insert(0, assmp)

    def add_assumptions_front(self, assmps: [AssumptionLattice]):
        """Adds multiple assumption to the front of the assumption list.

        :param assmps: list of assumptions to be added to the list of current assumptions
        """
        self._assmps = assmps + self.assmps

    def add_assmps_with_iter(self, iterations: int, assmps, pp):
        """Adds assumptions to the front of the assumption list and sets the iteration number.

        :param iterations: number of times the assumptions appear in the input file
        :param assmps: list of assumptions to be added to the list of current assumptions
        :param pp: program point of the first assumption
        """
        input_assmps = InputAssumptionLattice(iterations, assmps, pp)
        input_assmps.is_loop = True
        self._assmps.insert(0, input_assmps)

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'InputAssumptionLattice') -> bool:
        if self.infoloss and other.infoloss:
            return True
        if self.infoloss or other.infoloss:
            return False
        if len(self.assmps) != len(other.assmps):
            return False
        for assmp1, assmp2 in zip(self.assmps, other.assmps):
            if not assmp1.less_equal(assmp2):
                return False
        return True

    @copy_docstring(Lattice._join)
    def _join(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if self.infoloss:
            return self
        if other.infoloss:
            return self.replace(other)
        if len(self.assmps) == len(other.assmps) == 0:
            return self
        if self.join_as_loop:
            assert other.join_as_loop
            if len(self.assmps) > len(other.assmps):
                return self
            else:
                return self.replace(other)
        if len(self.assmps) != len(other.assmps) and not self.is_main:
            self.assmps.clear()
            self.infoloss = True
            return self
        if self.is_main:
            self.join_cases(other)
        else:
            new_assmps = []
            for assmp1, assmp2 in zip(self.assmps, other.assmps):
                if type(assmp1) != type(assmp2):
                    self.assmps.clear()
                    if not self.is_main:
                        self.infoloss = True
                    return self
                else:
                    new_assmps.append(deepcopy(assmp1).join(assmp2))
            self._assmps = new_assmps
        return self

    def join_cases(self, other):
        """Joins two InputAssumptionLattice. It unrolls assumptions in loops if necessary.

        [a] ⊔ [b] = [a ⊔ b]

        [N x [a]] ⊔ [b1, b2] = [a ⊔ b1, [(N-1) x [a]] ⊔ [b2]]

        [N x [a1], a2] ⊔ [M x [b1], b2] with N < M:  [N x [a1 ⊔ b1], [a2] ⊔ [(M-N) x [b1], b2]]

        :param other: other InputAssumptionLattice that should be joined with self
        """
        self_stack = self.assmps
        other_stack = other.assmps
        final_assmps = []
        while len(self_stack) > 0 and len(other_stack) > 0:
            curr_self = self_stack.pop(0)
            curr_other = other_stack.pop(0)
            self_assmp_lattice = isinstance(curr_self, AssumptionLattice)
            other_assmp_lattice = isinstance(curr_other, AssumptionLattice)
            if self_assmp_lattice and other_assmp_lattice:
                final_assmps.append(curr_self.join(curr_other))
            elif not self_assmp_lattice and not other_assmp_lattice:
                assert isinstance(curr_self, InputAssumptionLattice)
                assert isinstance(curr_other, InputAssumptionLattice)
                if curr_self.iterations == curr_other.iterations:
                    for assmp1, assmp2 in zip(curr_self.assmps, curr_other.assmps):
                        assmp1.join(assmp2)
                    final_assmps.append(curr_self)
                elif curr_self.iterations < curr_other.iterations:
                    copy_other_first = deepcopy(curr_other)
                    copy_other_first.iterations = curr_self.iterations
                    copy_other_second = deepcopy(curr_other)
                    copy_other_second.iterations -= curr_self.iterations
                    if copy_other_second.iterations == 1:
                        other_stack = copy_other_second.assmps + other_stack
                    else:
                        other_stack.insert(0, copy_other_second)
                    other_stack.insert(0, copy_other_first)
                    self_stack.insert(0, curr_self)
                else:
                    copy_self = deepcopy(curr_self)
                    copy_self.iterations = curr_other.iterations
                    curr_self.iterations -= curr_other.iterations
                    if curr_self.iterations == 1:
                        self_stack = curr_self.assmps + self_stack
                    else:
                        self_stack.insert(0, curr_self)
                    self_stack.insert(0, copy_self)
                    other_stack.insert(0, curr_other)
            elif self_assmp_lattice:
                assert isinstance(curr_other, InputAssumptionLattice)
                copy_other = deepcopy(curr_other)
                copy_other.iterations -= 1
                if copy_other.iterations == 1:
                    other_stack = copy_other.assmps + other_stack
                else:
                    other_stack.insert(0, copy_other)
                other_stack = curr_other.assmps + other_stack
                self_stack.insert(0, curr_self)
            else:
                assert isinstance(curr_self, InputAssumptionLattice)
                assert isinstance(curr_other, AssumptionLattice)
                copy_self = deepcopy(curr_self)
                copy_self.iterations -= 1
                if copy_self.iterations == 1:
                    self_stack = copy_self.assmps + self_stack
                else:
                    self_stack.insert(0, copy_self)
                self_stack = curr_self.assmps + self_stack
                other_stack.insert(0, curr_other)
        self._assmps = final_assmps

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Meet for {self} and {other} is not implemented.")

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Widening for {self} and {other} is not implemented.")
