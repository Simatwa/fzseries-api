from fzseries_api.hunter import Index
from fzseries_api.utils import souper

index = Index()


def write(name, contents):
    with open("recons" + "/" + name, "w") as fh:
        fh.write(souper(contents).prettify())


write("search_episode.html", index.search("Love", "episodes"))
