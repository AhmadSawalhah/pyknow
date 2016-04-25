from functools import update_wrapper
from itertools import product

from pyknow.factlist import FactList
from pyknow.fact import InitialFact, Fact
from pyknow.activation import Activation


class Rule:
    def __init__(self, *conds, salience=0):
        self.__fn = None

        if not conds:
            conds = (InitialFact(),)
        self.__conds = conds

        self.salience = salience

    def __call__(self, fst=None, *args, **kwargs):
        """
        Decorate or call a function.

        This function is going to be called twice.

        - The first call is when the decorator is been created. At this
          point we assign the función decorated to ``self.__fn`` and
          return ``self`` to be called the second time.

        - The second call is to execute the decorated function, se we
          pass all the arguments along.

        """
        if self.__fn is None:
            if fst is not None:
                self.__fn = fst
                return update_wrapper(self, self.__fn)
            else:
                raise AttributeError("Mandatory function not provided.")
        else:
            args = (tuple() if fst is None else (fst,)) + args
            return self.__fn(*args, **kwargs)

    def get_activations(self, factlist):
        """Return a tuple with the activations of this rule."""

        if not isinstance(factlist, FactList):
            raise ValueError("factlist must be an instance of FactList class.")
        else:
            def _activations():
                matches = []

                for cond in self.__conds:
                    if issubclass(cond.__class__, Rule):
                        acts = cond.get_activations(factlist)
                        if not acts:
                            break
                        for act in acts:
                            for fact in act.facts:
                                matches.append([fact])
                    elif isinstance(cond, Fact):
                        match = factlist.matches(cond)
                        if match:
                            matches.append(match)
                        else:
                            break
                else:
                    for match in product(*matches):
                        facts = tuple(sorted(set(match)))
                        if facts:
                            yield Activation(rule=self, facts=facts)

            return tuple(set(_activations()))


class NOT(Rule):
    def __init__(self, *conds, salience=0):
        super().__init__(*conds, salience=salience)

    def get_activations(self, factlist):
        """Returns the opposite of Rule.get_activations."""
        activations = super().get_activations(factlist)
        if activations:
            return tuple()
        else:
            fact = factlist.matches(InitialFact())
            if fact:
                factidx = fact[0]
                return tuple([Activation(rule=self, facts=(factidx, ))])
            else:
                return tuple()


class OR(Rule):
    def __init__(self, *conds, salience=0):
        super().__init__(*conds, salience=salience)

    def get_activations(self, factlist):
        """Return a tuple with the activations of this rule."""
        for cond in self._Rule__conds:
            matches = []

            for cond in self._Rule__conds:
                if issubclass(cond.__class__, Rule):
                    acts = cond.get_activations(factlist)
                    if not acts:
                        break
                    for act in acts:
                        for fact in act.facts:
                            matches.append([fact])
                elif isinstance(cond, Fact):
                    match = factlist.matches(cond)
                    if match:
                        matches.append(match)

        if matches:
            return tuple([Activation(rule=self,
                                     facts=[fact[0] for fact in matches])])
