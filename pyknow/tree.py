#!/usr/bin/env python

"""
    tree
    ----

    Helper classes to paralelize pyknow tasks
"""


class KETree:
    """
        Knowledge engine tree.

        Given a prestablished dictionary tree, this acts
        as an iterator that yields results from farthest to nearest
        element.
    """
    def __init__(self, tree):
        self.tree = tree
        self.finished = False
        self._tree = tree.copy()
        assert isinstance(self.tree, dict)
        assert self.is_valid_node(self.tree)

    @classmethod
    def is_valid_node(cls, node):
        """
            We walk over the entire tree ising
            its structure
        """
        try:
            assert isinstance(node, dict)
            assert 'node' in node
            if 'children' in node:
                assert isinstance(node['children'], list)
                for child in node['children']:
                    KETree.is_valid_node(child)
        except AssertionError:
            return False
        else:
            return True

    def pop_furthest_elements(self):
        """ Pop the latest childrens """

        def recurse(parent, results):
            """ Recursive magic """
            curr = []
            for num, child in enumerate(parent['children']):
                if child['children']:
                    recurse(child, results)
                else:
                    results.append(child['node'])
                    curr.append(num)

            for num in curr:
                parent['children'].pop(num - 1)

            return result

        result = []
        recurse(self._tree, result)
        return result

    def __iter__(self):
        return self

    def __next__(self):
        results = self.pop_furthest_elements()
        if self.finished:
            raise StopIteration()
        if not results:
            self.finished = True
            return [self.tree['node']]
        return results
