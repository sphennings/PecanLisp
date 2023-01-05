from collections import UserDict

from tokens import scan
from parser import parse, Collection, ExpressionType, Atom, S_Expression

import traceback
import readline  # noqa: F401
import sys

TRUE = Atom(ExpressionType.SYMBOL, True, None)
FALSE = Atom(ExpressionType.SYMBOL, False, None)
# FALSE.__bool__ = lambda x : False


class RuntimeError(Exception):
    pass


def convert(obj) -> S_Expression:
    """Takes an object and converts it into a lisp object"""
    if isinstance(obj, S_Expression):
        return obj
    elif isinstance(obj, bool):
        return TRUE if obj else FALSE
    elif isinstance(obj, list):
        return Collection(obj)
    elif isinstance(obj, str):
        return Atom(ExpressionType.SYMBOL, obj)
    else:
        raise Exception(f"New conversion target: {obj}")


class Env(UserDict):
    def __init__(self, initial_data=None, parent=None):
        self.parent = parent
        super().__init__(initial_data)

    def __getitem__(self, key):
        try:
            return self.data[key] if key in self.data else self.parent[key]
        except:
            raise RuntimeError(f"unbound variable: {key}")
    def set_var(self, key, value):
        if key in self.data:
            self.data[key] = value
        else:
            try:
                self.parent.set(key, value)
            except:
                raise RuntimeError(f"unbound variable: {key}")


global_env = Env()
global_env.update({"a": convert("aaaaaaa")})
global_env.update({"T": TRUE,
                   "F": FALSE})


def eval(x: S_Expression, env=global_env):
    if isinstance(x, Atom):
        if x.type == ExpressionType.SYMBOL:
            # Look up the symbol in the environment
            return env[x]

        elif x.type == ExpressionType.NUMBER:
            # Constant literal
            return x

    elif isinstance(x, Collection):
        match x.value:
            case Atom(value="quote") | Atom(value="q"), exp:
                # (quote exp) or (q exp)
                return exp

            case Atom(value="atom?"), exp:
                # (atom? exp)
                return convert(isinstance(eval(exp, env), Atom))

            case Atom(value="eq?"), exp1, exp2:
                # (eq? exp1 exp2)
                v1, v2 = eval(exp1, env), eval(exp2, env)
                return convert((isinstance(v1, Atom) and (v1 == v2)))

            case Atom(value="car"), exp:
                # (car exp)
                return eval(exp, env)[0]

            case Atom(value="cdr"), exp:
                # (car exp)
                return convert(eval(exp, env)[1:])

            case Atom(value="cons"), exp1, exp2:
                # (cons exp1 exp2)
                return convert([eval(exp1, env)] + list(eval(exp2, env)))

            case Atom(value="cond"), *exps:
                # (cond (p1 e1) ... (pn en))
                for (p, e) in exps:
                    print(p, e)
                    if eval(p, env):
                        return eval(e, env)

            case Atom(value="null?"), exp:
                # (null? exp)
                return convert(eval(exp, env) == [])

            case Atom(value="if"), test, conseq, alt:
                # (if test conseq alt)
                if eval(test, env):
                    return eval(conseq, env)
                else:
                    return eval(alt, env)

            case Atom(value="set!"), var, exp:
                # (set! var exp)
                env.set_var(var, convert(eval(exp, env)))

            case Atom(value="define"), var, exp:
                # (define var exp)
                env[var] = eval(exp, env)

            case Atom(value="lambda"), vars, exp:
                # (lambda (var*) exp)
                return lambda *args: eval(exp, Env(zip(vars, args), env))
            case _:
                proc, *exps = [eval(exp, env) for exp in x.value]
                return proc(*exps)


def test(src):
    print(f"Testing: {src}")
    tokens = scan(src)
    ast = parse(tokens)
    for exp in ast:
        print(eval(exp))


def repl(prompt="lisp> "):
    "A read eval print loop."
    while True:
        try:
            ast = parse(scan(input(prompt)))
            for exp in ast:
                val = eval(exp)
                if val is not None:
                    print(str(val))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting lisp")
            sys.exit()
        except:
            print("An error occurred. Here's the Python stack trace:")
            traceback.print_exc()


if __name__ == "__main__":
    # test("(quote aaa)")
    # test("(q aaa)")
    # test("(atom? (quote aaa))")
    # test("(atom? (quote (a a)))")
    # test("(eq? (quote a) (quote a))")
    # test("(eq? (quote a) (quote b))")
    # test("(car (quote (a b c)))")
    # test("(cdr (quote (a b c)))")
    # test("(cons (quote a) (quote (a b c)))")
    # test("(cons (q (a b c)) (q (1 23)))")
    # test("(cond ((eq? 1 2) (q a)) ((eq? 2 2) (q b)))")
    # test("(null? (q ()))")
    # test("(null? (q a))")
    # test("(if (eq? 1 1) (q a) (q b))")
    # test("(if (eq? 1 3) (q a) (q b))")
    # test("a")
    # test("(eq? a (q aaaaaaa))")
    # test("(set! a 55)")
    # test("a")
    # test("(define b 55)")
    # test("(eq? a b)")
    # test("(define cmp (lambda (a b) (eq? a b)))")
    # # test("(cmp 1 1)")
    # test("(cmp cmp cmp)")
    # test("(eq? 1 1) (eq? 2 2)")
    repl()
