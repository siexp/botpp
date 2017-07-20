import argparse
import json
import requests
import os
import timeit

from multiprocessing.dummy import Pool as ThreadPool 

# globals that probably will not change 
# until script done
uid = None
sid = None
headers = None
voted = None

postPerPage = 20

def vote( uri, userId, value ) :
    if ( userId != uid ) :
        resp = requests.post( uri, data = { "vote": value }, headers=headers ).json()
        print( resp )

def voter( post ) :            
    # upvote each post that not belongs to you
    postId = str( post[ 'id' ] )
    postUserId = str( post['user']['id'] )
    uri = "https://dirty.ru/api/posts/" + postId + "/vote/"
    if postId not in voted :
        vote( uri, postUserId, 1 )
        voted[ postId ] = json.loads('[]')                
    else :
        print( 'Already voted <' + postId + '>')
    
    resp = requests.get( "https://dirty.ru/api/posts/" + postId + "/comments/" )
    comments = resp.json()[ 'comments' ]
    # upvote each comment in the post
    for comment in comments :
        commentId = str( comment[ 'id' ] )
        commentUserId = str( comment['user']['id'] )
        uri = "https://dirty.ru/api/comments/" + commentId + "/vote/"
    
        if commentId not in voted[ postId ] :
            vote( uri, commentUserId, 1 )
            voted[ postId ].append( commentId )
        else :
            print( 'Already voted <' + postId + ':' + commentId + '>' )

def main( user, password, subdomain ) : 
    # login
    auth = { "username": user, "password": password }
    resp = requests.post( "https://dirty.ru/api/auth/login/", auth )

    global uid
    uid = resp.json()[ 'uid' ]
    global sid
    sid = resp.json()[ 'sid' ]
    global headers
    headers = { "X-Futuware-UID": uid, "X-Futuware-SID": sid }

    global voted 
    voted = loadCache()

    # get list of all posts of subdomain
    pageId = 1
    while True :
        print( "Processing page #" + str( pageId ) + " of subdomain <" + subdomain + ">" )
        resp = requests.get( "https://dirty.ru/api/domains/" + subdomain + "/posts/?page=" + str( pageId ) + ";per_page=" + str( postPerPage ) + ";sorting=date_created" )
        posts = resp.json()[ 'posts' ]
        
        # make the Pool of workers
        pool = ThreadPool( postPerPage ) 

        # open the urls in their own threads
        # and return the results
        results = pool.map( voter, posts )

        # close the pool and wait for the work to finish 
        pool.close() 
        pool.join() 

        saveCache( voted )
        if len( posts ) != postPerPage :
            break
        
        pageId += 1       

def loadCache() :
    data = json.loads('{}')
    if os.path.exists( 'cache.json' ) :
        with open('cache.json') as cache :
            data = json.load( cache )

    return data

def saveCache( cache ) :
    with open('cache.json', 'w') as outfile:
        json.dump( cache, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser( description='PyScrip that allows to upvote each post and each comment in subdomain' )

    parser.add_argument( 'user', help = 'your username' )
    parser.add_argument( 'password', help = 'your password' )
    parser.add_argument( 'subdomain', help = 'subdomain to process' )

    args = parser.parse_args()

    startTime = timeit.default_timer()
    main( args.user, args.password, args.subdomain )
    elapsed = timeit.default_timer() - startTime

    print( "Scripts run time: " + elapsed + "s" )
