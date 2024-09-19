import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP | VP | NP PP | S Conj S | NP AdjP | NP AdvP | NP AdjP PP | VP PP AdjP | S P S

NP -> N | NP VP | Det NP
VP -> V | VP NP | VP Det NP
PP -> P | PP NP | PP AdjP
AdjP -> Adj | Det AdjP | AdjP NP | Adj AdjP
AdvP -> Adv | AdvP VP | PP AdvP
"""



grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    tokens = nltk.word_tokenize(sentence)
    new_tokens = []

    for token in tokens:
        if any(char.isalpha() for char in token):
            new_tokens.append(token.lower())

    return new_tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    np = []

    def np_in_tree(tree):
        for subtree in tree:

            if not(isinstance(subtree, nltk.tree.Tree)):
                continue

            if subtree.label() == 'NP' and not 'NP' in str(subtree)[3:]:
                np.append(subtree)
                continue

            np_in_tree(subtree)

    np_in_tree(tree)

    return np


if __name__ == "__main__":
    main()
