from collections import namedtuple
from collections.abc import Mapping
import dis

from pyknow.rule import PatternConditionalElement
from pyknow.rule import LiteralPCE, PredicatePCE, WildcardPCE
from pyknow.rule import ANDPCE, ORPCE, NOTPCE
from .abstract import Check


class TypeCheck(Check, namedtuple('_TypeCheck', ['fact_type'])):

    _instances = dict()

    def __new__(cls, fact_type):
        if fact_type not in cls._instances:
            cls._instances[fact_type] = super().__new__(cls, fact_type)
        return cls._instances[fact_type]

    def __call__(self, fact):
        return type(fact) == self.fact_type


class SelfBindedCheck(Check, namedtuple('_SelfBindedCheck', ['items'])):

    _instances = dict()

    def __new__(cls, items):
        if items not in cls._instances:
            cls._instances[items] = super().__new__(cls, items)
        return cls._instances[items]

    def __call__(self, fact):
        try:
            return set(fact[k] for k in self.items) == 1
        except KeyError:
            return False


class FeatureCheck(Check,
                   namedtuple('_FeatureCheck',
                              ['what', 'how', 'check', 'lhs'])):

    _instances = dict()

    def __new__(cls, what, how):
        if not isinstance(how, PatternConditionalElement):
            raise TypeError(
                "Check object accepts PatternConditionalElements only.")
        else:
            key_a = type(how)
            if key_a is LiteralPCE:
                key_b = how[0]
            elif key_a is PredicatePCE:
                key_b = tuple(dis.get_instructions(how[0]))
            elif key_a is WildcardPCE:
                key_b = how
            elif key_a is NOTPCE:
                key_b = FeatureCheck(what, how[0])
            elif key_a in (ANDPCE, ORPCE):
                key_b = tuple([FeatureCheck(what, h) for h in how])
            else:
                raise TypeError("Unknown PCE type.")

            key = (what, key_a, key_b)

            if key not in cls._instances:
                if key_a is LiteralPCE:
                    lhs = how[0]

                    def check(v, lhs):
                        return lhs == v
                elif key_a is PredicatePCE:
                    lhs = how[0]

                    def check(v, lhs):
                        return lhs(v)
                elif key_a is WildcardPCE:
                    lhs = how
                    if not how:

                        def check(v, lhs):
                            return True
                    else:

                        def check(v, lhs):
                            return {lhs[0]: v}
                elif key_a is NOTPCE:
                    lhs = key_b

                    def check(v, lhs):
                        return not lhs(v, is_fact=False)
                elif key_a is ANDPCE:
                    lhs = key_b

                    def check(v, lhs):
                        value = dict()
                        for subcheck in lhs:
                            subres = subcheck(v, is_fact=False)
                            if subres is False:
                                break
                            elif subres is True:
                                pass
                            elif isinstance(subres, Mapping):
                                value.update(subres)
                            else:
                                raise TypeError('Bad check value.')
                        else:
                            if not value:
                                return True
                            else:
                                return value
                        return False
                elif key_a is ORPCE:
                    lhs = key_b

                    def check(v, lhs):
                        for subcheck in lhs:
                            subres = subcheck(v, is_fact=False)
                            if subres:
                                return subres
                        else:
                            return False
                else:  # noqa
                    pass

                cls._instances[key] = super(Check, cls).__new__(
                    cls,
                    what,
                    how,
                    check,
                    lhs)

            return cls._instances[key]

    def __call__(self, data, is_fact=True):
        if is_fact:
            try:
                # Value is always inside a LiteralPCE
                record = data[self.what][0]
            except KeyError:
                return False
        else:
            record = data

        return self.check(record, self.lhs)
