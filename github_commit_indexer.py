#!/usr/bin/python3

try: 
    import os, sys, requests
    import argparse, json
    import datetime as dt
    import configparser
    from elasticsearch import Elasticsearch
    from github import Github
    from string import ascii_letters
    
    print("All libraries/modules loaded as expected !!!!! ")
except Exception as err:
    print("Missing Modules =====> %s" %err)
    print("Kindly installed using pip3 install <pip-package-name>")
    sys.exit(1)


parser=argparse.ArgumentParser(prog='Github_commit_indexer',
                               epilog=''' NOTE: This script basically pull commits from a public github repo,
then index each commit before storing them into elastic search deployment clould server
''')

parser.add_argument('--GithubUser', nargs='?', default='RockstarLang', help= 'Github user account')
parser.add_argument('--repo', nargs='?', default='rockstar', help= 'Github repo')



if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    #sys.exit(1)    
args=parser.parse_args()


def to_stderr(msg):
    print(msg, file=sys.stderr, flush=True)

def error(msg):
    to_stderr('ERROR: ' + msg)
    sys.exit(1)

def datetime_formater(unformated_datetime):
    '''
    This function basically convert daytime to human readable format
    '''
    date_time = unformated_datetime.split("T")
    date = date_time[0].split("-")
    time = date_time[1].rstrip(ascii_letters).split(":")
    formated_datetime = dt.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    return formated_datetime.strftime("%d-%b-%Y %H:%M:%S")


def Elastic_Search(elk_object, commit_document,indx):
    try:
        '''
        Ingesting commit history document to ElasticServer deployment
        '''
        #elk_object.indices.create(index = indx, ignore=400)
        ingest_status = elk_object.index(index=indx, body=commit_document) 
        
        if ingest_status["result"] != "created" and int(ingest_status["_shards"]["failed"]) == 1:
            print(json.dumps(commit_document, indent = 2))
            error("Ingesting to ElasticServer deployment failed for last committed indexed document \n ")     
        elk_object.indices.refresh(index = indx)  
    except Exception as err:
        error(str(err))

def commit_info(api_commit_url, ElasticSearch):
    '''
    This function basically pull out needed info to be ingested as index documents for cloud elastic search
    '''
    global document
    global count
    try:    
        commit_data = requests.get(api_commit_url).json()
        document.setdefault("Date", datetime_formater(commit_data["commit"]["author"]["date"]))
        document.setdefault("Username", commit_data["author"]["login"])
        document.setdefault("Message", commit_data["commit"]["message"].replace("\n\n", " "))
        Elastic_Search(ElasticSearch, document, document["Username"])
        print(json.dumps(document, indent = 2))
        print("indexed document ingested into clould deployment successfully !!!!!")
        print("\n\n")
        document = {}
    except Exception as err:
        print("\n\n")
        error(str("%s: %s" %(err,commit_data["message"])))


if __name__ == '__main__':
    try:
        document = {}
        '''
        Parse login credential for Github and ElasticSearch
        '''
        login_config_parse = configparser.ConfigParser()
        login_config_parse.read('login_credential.ini')
        
    
        # verify that Elastic login_credential.ini file exist#
        if not os.path.isfile("login_credential.ini"):
            print('\n\n### Kindly create a basic authentication file named "login_credential.ini"')
            print("[ELASTIC]")
            print('cloud_id = "DEPLOYMENT_NAME:CLOUD_ID_DETAILS" ')
            print('user = Username' )
            print('Password = Password  \n\n\n')
            print('[GITHUB]')
            print('login_or_token = Github Person Access Token')
            sys.exit(1)
            
        '''
        Connect to Github repo
        kindly note that unauthenticated API calls are rate limited to 60 requests/hour
        '''
        GH = Github(login_or_token=login_config_parse['GITHUB']['login_or_token'])
        github_object = GH.get_user(args.GithubUser)
        GH_repo = github_object.get_repo(args.repo)
        
        '''
        Connect to elastic search cloud deployment using cloud_id & http_auth method
        '''
        ES = Elasticsearch(
            cloud_id = login_config_parse['ELASTIC']['cloud_id'],
            http_auth = (login_config_parse['ELASTIC']['user'],  login_config_parse['ELASTIC']['password'])
            )
        #print(json.dumps(ES.info(), indent = 2))
        
        '''
        Verify successfull communication with ElasticSearch Deployment
        '''
        if ES.ping() is not True:
            print("Kindly verify your deployment status/login credential, refers to the below official ElasticSearch documentation on basic authentication")
            print("https://www.elastic.co/guide/en/cloud/current/ec-getting-started-python.html")
            
        '''
         Note:- Wont scale nicely based on github API rate-limiting with limited number of request/hour 
        ''' 
        commit = GH_repo.get_commits()
        count = 0
        '''
        This loop over commit SHA paginated list, then parse each commit hash signed with SHA to repos commit API url
        '''
        for commit_hash in commit:
            commit_sha = str(commit_hash).split('"')[1]
            commit_url = GH_repo.commits_url.split("{/sha}")[0]+"/{}".format(commit_sha)
            commit_info(commit_url, ES)
            count+=1
        print("Process now completed!!!!!!")    
    except Exception as err:
        error(str(err))