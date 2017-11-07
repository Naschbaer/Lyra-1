# class IntAexp:
#     def __init__(self, i):
#         self.i = i
#
#     def eval(self, _):
#         return self.i
#
#
# class VarAexp:
#     def __init__(self, name):
#         self.name = name
#
#     def eval(self, env):
#         if self.name in env:
#             return env[self.name]
#         else:
#             return 0
#
#
# t = IntAexp(3)
# x = VarAexp('x')
# y = VarAexp('y')

class Aexp:

    def eval(self, env):
        pass


class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i

    def eval(self, _):
        return self.i


class VarAexp(Aexp):
    def __init__(self, name):
        self.name = name

    def eval(self, env):
        if self.name in env:
            return env[self.name]
        else:
            return 0


t = IntAexp(3)
x = VarAexp('x')
y = VarAexp('y')


class Bexp:
    pass


class RelopBexp(Bexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)
        if self.op == '<':
            value = left_value < right_value
            return value
        elif self.op == '<=':
            value = left_value <= right_value
            return value
        elif self.op == '>':
            value = left_value > right_value
            return value
        elif self.op == '>=':
            value = left_value >= right_value
            return value
        elif self.op == '=':
            value = left_value == right_value
            return value
        elif self.op == '!=':
            value = left_value != right_value
            return value
        else:
            raise RuntimeError('unknown operator: ' + self.op)


f = IntAexp(4)
e = IntAexp(8)
c = RelopBexp('<', f, e)
c.eval(dict())


class Statement:
    pass


class AssignStatement(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp

    def eval(self, env):
        value = self.aexp.eval(env)
        env[self.name] = value


class CompoundStatement(Statement):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def eval(self, env):
        self.first.eval(env)
        self.second.eval(env)


y3 = AssignStatement('y', t)
xy = AssignStatement('x', y)

compound = CompoundStatement(y3, xy)
