#python script to fetch the commit history and index all commits in Elastic Search.
Issue:
For an inexplicable reason, our product owner
really wants all commit activity from this public
repo (https://github.com/RockstarLang/rockstar) to be available as separate documents in
Elastic search
They further specified that each document
should include:
- date of each commit
- username of the committer
- commit message
