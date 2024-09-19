import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    distribution = {}

    links = corpus[page]

    if links:

        for link in corpus:
            distribution[link] = (1 - damping_factor) / len(corpus)
        
        probability = damping_factor / len(corpus[page])

        for link in corpus[page]:
            distribution[link] += probability
    
    else:
        probability = 1 / len(corpus)

        for link in corpus:
            distribution[link] = probability

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    page = random.choice(list(corpus.keys()))
    distribution = {page: 0.0 for page in corpus}

    for i in range(n):
        trans_distribution: dict = transition_model(corpus, page, damping_factor)
        page = random.choices(list(trans_distribution.keys()), trans_distribution.values())[0]

        distribution[page] += 1/n
    
    return distribution


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # assign default probability for each page
    N = len(corpus)
    probability = 1 / N
    ranks = {page: probability for page in corpus}

    # update corpus if a page has no links
    updated_corpus = {}
    for page in corpus:
        if not corpus[page]:
            updated_corpus[page] = set(corpus.keys())
        else:
            updated_corpus[page] = corpus[page]

    # threshold
    threshold = 0.001

    while True:
        new_rank = {page: 0 for page in corpus}
        previous_rank = ranks

        for page in corpus.keys():
            rank = (1 - damping_factor) / N

            summation = 0

            for sub_page in corpus.keys():
                if page in corpus[sub_page]:
                    summation += ranks[sub_page] / len(corpus[sub_page])
            
            rank += damping_factor * summation
            new_rank[page] = rank

        ranks = new_rank

        # threshold
        if all(abs(old - new) <= threshold for old, new in zip(previous_rank.values(), new_rank.values())):
            break

    return ranks


if __name__ == "__main__":
    main()
