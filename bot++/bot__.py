import argparse
import requests

uid = None
sid = None
headers = None

def upvote( uri, userId ) :
    if ( userId != uid ) :
        resp = requests.post( uri, data = { "vote": 1 }, headers=headers )
        print( resp.text )

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

    # get list of all posts of subdomain
    resp = requests.get( "https://dirty.ru/api/domains/" + subdomain + "/posts/" )
    posts = resp.json()[ 'posts' ]
    
    for post in posts :        
        # upvote each post that not belongs to you
        postId = str( post[ 'id' ] )
        postUserId = str( post['user']['id'] )
        uri = "https://dirty.ru/api/posts/" + postId + "/vote/"
        upvote( uri, postUserId )            

        resp = requests.get( "https://dirty.ru/api/posts/" + postId + "/comments/" )
        comments = resp.json()[ 'comments' ]
        # upvote each comment in the post
        for comment in comments :
            commentId = str( comment[ 'id' ] )
            commentUserId = str( comment['user']['id'] )
            uri = "https://dirty.ru/api/comments/" + commentId + "/vote/"
            upvote( uri, commentUserId )            

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description='PyScrip that allows to upvote each post and each comment in subdomain' )
    
    parser.add_argument( 'user', help = 'your username' )
    parser.add_argument( 'password', help = 'your password' )
    parser.add_argument( 'subdomain', help = 'subdomain to process' )

    args = parser.parse_args()
    main( args.user, args.password, args.subdomain )
