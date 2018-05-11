"""
Alias Lattices
==============

Lattices to be used for **alias analysis on numpy ndarrays**.

:Authors: Sebastien Foucher
"""

from lyra.abstract_domains.lattice import KindMixin, Lattice
from lyra.core.utils import copy_docstring

from typing import List

from itertools import count


class AliasLattice(KindMixin):
    """Alias lattice. The bottom interval represents an empty set.

    The default lattice element is ``[]`` (array is not allocated).

    .. document private methods
    .. automethod:: AliasLattice._less_equal
    .. automethod:: AliasLattice._meet
    .. automethod:: AliasLattice._join
    .. automethod:: AliasLattice._widening
    """

    def __init__(self, alias: List = []):
        super().__init__()
        self._element = alias
        self._object_id_generator = ObjectID()
    @property
    def element(self):
        """Current lattice element."""
        return self._element

    def __repr__(self):
        return str(self.element)
    
    def allocate(self):
        """New object allocated. The lattice has only one element at this state"""
        self._element = [ObjectID().get_obj_id()]
        return self

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        """The bottom lattice element is ``[]`` (array is not allocated)."""
        self.replace(AliasLattice())
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``['...']`` (all locations possible)."""
        self.replace(AliasLattice(['...']))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self):
        #empty sequence is FALSE
        return not self.element

    @copy_docstring(Lattice.is_top)
    def is_top(self):
        if len(self.element) == 1:
            return self.element[0] == '...'
        else:
            return False

    @copy_docstring(Lattice.less_equal)
    def _less_equal(self, other: 'AliasLattice') -> bool:  
        return all(elem in other.element for elem in self.element)

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'AliasLattice') -> 'AliasLattice':
        self.replace(AliasLattice(list(set(self.element).intersection(other.element))))
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'AliasLattice') -> 'AliasLattice':
        self.replace(AliasLattice(self.element + other.element))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'AliasLattice') -> 'AliasLattice':
        return self._join(other)
    
    @copy_docstring(KindMixin.kind)
    def kind(self):
        if self.is_bottom:
            return KindMixin.Kind.BOTTOM
        elif self.is_top:
            return KindMixin.Kind.TOP
        else:
            return KindMixin.Kind.DEFAULT

class ObjectID():
    _ids = count(0)

    def __init__(self):
        self._ids = next(self._ids)
        
    def get_obj_id(self):
        return self._ids