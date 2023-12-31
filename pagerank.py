import os
import random
import re
import sys
import math

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
    prob = 0
    prob_dist = {
        var : prob 
        for var in corpus.keys() 
    }
    
    linked_prob = damping_factor / len(corpus[page])
    for p in corpus[page]:
        prob_dist[p] = linked_prob

    for p in corpus.keys():
        prob_dist[p] += (1 - damping_factor)/len(corpus)

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    rank = 0
    pagerank  = {
        var: rank
        for var in corpus.keys()
    }

    rand = random.randint(0,len(corpus)-1)
    page = list(corpus.keys())[rand] # Take the first page randomly
    prob_dist = transition_model(corpus,page,damping_factor) # Initialize a transition model
    pagerank[page] += 1
    for sample in range(n):
        page = random.choices(list(prob_dist.keys()), weights=[round(val*100, 6) for val in prob_dist.values()], k=1)[0]
        prob_dist = transition_model(corpus,page,damping_factor)
        pagerank[page] += 1

    for p in pagerank:
        pagerank[p] /= n

    return pagerank 


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    initial_rank = 1 / N
    pagerank = {page: initial_rank for page in corpus.keys()}
    updated_pagerank = {page: 0 for page in corpus.keys()}

    repeat = True
    while repeat:
        repeat = False
        for page in pagerank.keys():
            total_contribution = 0
            for linking_page, linked_pages in corpus.items():
                num_links = len(linked_pages)
                if num_links == 0:
                    num_links = N
                if page in linked_pages:
                    total_contribution += pagerank[linking_page] / num_links
            
            new_rank = (1 - damping_factor) / N + damping_factor * total_contribution
            new_rank = round(new_rank, 4)  # Round after calculations
            
            # Stop iteration when the values changed no more than 0.001
            if round(abs(new_rank - pagerank[page]),4) > 0.001:
                repeat = True

            updated_pagerank[page] = new_rank

        # Normalize ranks to sum to 1
        for page in updated_pagerank.keys():
            updated_pagerank[page] = math.floor(updated_pagerank[page]*10000)/10000
        
        pagerank = updated_pagerank.copy()

    return pagerank


if __name__ == "__main__":
    main()
