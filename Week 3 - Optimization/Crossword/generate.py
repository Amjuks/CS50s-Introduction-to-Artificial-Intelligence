import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        # loop through every variable
        for variable, domain in self.domains.items():

            values_to_remove = set()

            # loop through all values in its domain
            for value in domain:

                # remove values if they are not consistent
                if not len(value) == variable.length:
                    values_to_remove.add(value)

            for value in values_to_remove:
                self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        # set default value for revise
        revised = False

        # overlap
        overlap = self.crossword.overlaps[x, y]

        x_domain = copy.deepcopy(self.domains[x])
        # loop through domain of x
        for x_value in x_domain:
            
            satisfies = True

            # loop through domain of y
            for y_value in self.domains[y]:
                if x_value[overlap[0]] != y_value[overlap[1]]:
                    satisfies = False
                    revised = True
            
            # delete value from x domain if the constrain  is satisfied
            if satisfies:
                self.domains[x].remove(x_value)
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # initial list with all arcs
        if arcs is None:
            queue = [(x, y) for x in self.domains.keys() for y in self.domains.keys() if x != y]

        while arcs:
            # dequeue
            arc = arcs.pop()

            if self.revise(arc[0], arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    return False

                for z in self.crossword.neighbors(arc[0]):
                    if not z == arc[1]:
                        queue.append((z, arc[0]))

        return True
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        keys = assignment.keys()

        for variable in self.domains.keys():
            if variable not in keys:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        distinct_values = []

        for key, value in assignment.items():

            # distinct words
            if value in distinct_values:
                return False
            
            else:
                distinct_values.append(value)

            # check length
            if len(value) != key.length:
                return False

            # check neighbors
            neighbors = self.crossword.neighbors(key)
            for neighbor in neighbors:

                if neighbor in assignment.keys():
                    x, y = self.crossword.overlaps[key, neighbor]
                    if assignment[key][x] != assignment[neighbor][y]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        heuristic = {}
        neighbors = self.crossword.neighbors(var)
        values = self.domains[var]
        keys = assignment.keys()

        for value in values:

            n = 0
            
            for neighbor in neighbors:
                if neighbor in keys:
                    continue

                x, y = self.crossword.overlaps[var, neighbor]

                for neighbor_value in self.domains[neighbor]:
                    if value[x] != neighbor_value[y]:
                        n += 1
            
            heuristic[value] = n
        
        return sorted(heuristic.keys(), key=lambda x: heuristic[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        keys = assignment.keys()
        unassigned = [variable for variable in self.domains.keys() if variable not in keys]
        unassigned = sorted(unassigned, key=lambda var: len(self.domains[var]))
        
        if len(unassigned) == 1:
            return unassigned[0]
        
        degrees = {var: len(self.crossword.neighbors(var)) for var in unassigned}
        lowest_degree = min(degrees.values())
        degrees = {key: value for key, value in degrees.items() if value == lowest_degree}

        return list(degrees.keys())[0]

        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        # check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)

                if result is not None:
                    return result
                
            assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else: 
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()