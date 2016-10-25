from collections import deque


class Agenda:
    """

    Collection of activations that handles its execution state.

    .. note::
       Extracted from clips documentation: ``The agenda is a collection
       of activations which are those rules which match pattern entities``

    """
    def __init__(self):
        self.activations = deque()
        self.executed = set()

    def get_next(self):
        """
        Returns the next activation, removes it from
        activations list and adds it to executed activations list

        """
        try:
            act = self.activations.popleft()
            self.executed.add(act)
            return act
        except IndexError:
            return None

    def remove_from_fact(self, fact):
        """
        Remove a matching activation against a specific fact

        """
        activations_to_remove = []
        for activation in self.activations:
            if activation.facts == (fact,):
                activations_to_remove.append(activation)
        for activation in activations_to_remove:
            self.activations.remove(activation)
