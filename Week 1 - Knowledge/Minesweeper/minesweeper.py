import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) == self.count:
            return self.cells
        
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return self.cells

        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # add cell to the set of moves made
        self.moves_made.add(cell)

        # add cell to the set of safes
        self.safes.add(cell)

        # get the nearby cells of the cell
        neighbours = self.nearby_cells(cell)

        # add a new sentence to KB with known knowledge
        known_cells = set()

        # gather all the nearby cells that are known
        for cell in neighbours:
            if cell in self.mines or cell in self.safes:
                known_cells.add(cell)

                if cell in self.mines:
                    count -= 1
        
        neighbours -= known_cells

        # add a new sentence
        sentence = Sentence(neighbours, count)
        self.knowledge.append(sentence)

        # store all known mines and safes
        mines = set()
        safes = set()
        for s in self.knowledge:
            mines = mines.union(s.known_mines())
            safes = safes.union(s.known_safes())

        # mark all mines and safes
        for mine in mines:
            self.mark_mine(mine)
        for safe in safes:
            self.mark_safe(safe)

        # remove all empty sentences
        for s in self.knowledge:
            if s.cells == set():
                self.knowledge.remove(s)

        # add new sentences to KB based on known knowledge
        self.draw_inference(self.knowledge)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # iterate through all known safe cells
        for move in self.safes:

            # check if the move hasn't been made, and return it
            if move not in self.moves_made:
                return move

        # return None since no safe moves are found
        return None
    
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # create a set of all possible moves
        possible_moves = set(itertools.product(range(8), range(8))) - self.moves_made - self.mines

        # if no moves are found, return None
        if not possible_moves:
            return None

        # return a random possible move
        move = random.choice(list(possible_moves))
        return move
    
    def nearby_cells(self, cell):
        """
        Return nearby cells of a given cell
        """

        # set i and j to i and j values of the cell
        i, j = cell

        # nearby cells of the cell
        neighbours = {
            (i + di, j + dj)
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if di or dj
            if 0 <= i + di < self.height
            if 0 <= j + dj < self.width
        }

        return neighbours
    
    def draw_inference(self, KB):
        """
        Draw new inferences from known sentences
        """

        # iterate through all possible pairs
        for sentence, other in itertools.product(KB, KB):

            # continue if the elements of pair are alike or the pair is already checked
            if sentence == other:
                continue
            
            # add knowledge if possible by subset method
            if sentence.cells.issubset(other.cells):
                s = Sentence(other.cells - sentence.cells, other.count - sentence.count)
                self.knowledge.append(s)

        # eliminate duplicates
        knowledge = []
        [knowledge.append(x) for x in self.knowledge if x not in knowledge and not x == Sentence(set(), 0)]
        self.knowledge = knowledge