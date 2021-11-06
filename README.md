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

View from elastic cloud to test for the below user.

- 1.	Dylanbeattie
- 2.	Mikesep
    And the test was ok with 200. You can see that if you scroll down. 


![GIT1](https://user-images.githubusercontent.com/37187773/140616971-f3a3e53f-97ac-447c-9b97-a595053d10ee.jpg)
![GIT2](https://user-images.githubusercontent.com/37187773/140616777-6234aafe-9b0f-4b59-adbe-f41f7535b8e5.png)
![GIT3](https://user-images.githubusercontent.com/37187773/140616780-ac1d5a3b-b2f0-4098-ac86-47fd1a6e9028.png)
![GIT4](https://user-images.githubusercontent.com/37187773/140616781-e0788cfc-d526-4b6f-ba9c-100fb9d1cce2.png)
