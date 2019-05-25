"""
MIT License

Copyright (c) 2010-2017 Peter Norvig

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://github.com/norvig/pytudes
"""

import random
from collections import deque, namedtuple


def Edge(node1, node2):
    return tuple(sorted([node1, node2]))


def random_tree(nodes: set, neighbors: callable, pop: callable) -> [Edge]:
    """Repeat: pop a node and add Edge(node, nbr) until all nodes have been added to tree."""
    tree = []
    root = nodes.pop()
    frontier = deque([root])
    while nodes:
        node = pop(frontier)
        nbrs = neighbors(node) & nodes
        if nbrs:
            nbr = random.choice(list(nbrs))
            tree.append(Edge(node, nbr))
            nodes.remove(nbr)
            frontier.extend([node, nbr])
    return tree


Maze = namedtuple("Maze", "width, height, edges")


def neighbors4(square):
    """The 4 neighbors of an (x, y) square."""
    (x, y) = square
    return {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}


def squares(width, height):
    """All squares in a grid of these dimensions."""
    return {(x, y) for x in range(width) for y in range(height)}


def random_maze(width, height, pop=deque.pop):
    """Use random_tree to generate a random maze."""
    nodes = squares(width, height)
    tree = random_tree(nodes, neighbors4, pop)
    return Maze(width, height, tree)
