import fzseries_api.hunter as hunters
import fzseries_api.handlers as handlers
import fzseries_api.models as models


def test_episode_search_handler():
    html_contents = hunters.Index().search("love", "episodes")
    handlers.episode_search_results_handler(html_contents)


import re

all = (
    """
<small>
The episode begins with a flashback to the year 2004, where John Casey is involved with a female Russian named Ilsa, who claims she is a photo journalist. Later, in present day, Ilsa returns with a fiancé, named Victor Federov. Things get complicated when it is revealed that Ilsa is a French spy.
<br/><br/>Stars: Zachary Levi,Yvonne Strahovski,Joshua Gomez
<br/>Director(s): Josh Schwartz,Chris Fedak
<br/>Writer(s): Josh Schwartz,Chris Fedak
</small>
""",
    """
<small>The episode begins with a flashback to the year 2004, where John Casey is involved with a female Russian named Ilsa, who claims she is a photo journalist. Later, in present day, Ilsa returns with a fiancé, named Victor Federov. Things get complicated when it is revealed that Ilsa is a French spy.<br/><br/>Stars: Zachary Levi,Yvonne Strahovski,Joshua Gomez<br/>Director(s): Josh Schwartz,Chris Fedak<br/>Writer(s): Josh Schwartz,Chris Fedak</small>
""",
)[1]

res1 = re.sub("\n\n", "\n", re.sub(r"<\W?\w*/?>", "\n", all)).strip().split("\n")

print(res1)
# test_episode_search_handler()
