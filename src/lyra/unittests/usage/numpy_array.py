from typing import *
from numpy import ndarray, arange

alist: List[str] = ['a']
#alist: List[str] = alist.append('append_test')
array: ndarray = [1]

english: bool = bool(input())
math: bool = bool(input())
science: bool = bool(input())
bonus: bool = bool(input())
passing: bool = True
#something: str = 'test'

# RESULT: alist -> Dead, array -> Live, english -> Live, math -> Live, science -> Dead, bonus -> Live, passing -> Live

if not english:
    english: bool = False         # error: *english* should be *passing*
if not math:
    passing: bool = False or bonus
if not math:
    passing: bool = False or bonus   # error: *math* should be *science*

print(passing)
# RESULT: alist -> Dead, array -> Live, english -> Dead, math -> Dead, science -> Dead, bonus -> Dead, passing -> Dead
print(array[0])
