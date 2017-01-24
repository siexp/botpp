import requests
import json
import sys

def main( args ) :
    if len( args ) != 3 :
        return

    auth = { "username": args[ 1 ], "password": args[ 2 ] }
    resp = requests.post( "https://dirty.ru/api/auth/login/", auth )

    uid = resp.json()[ 'uid' ]
    sid = resp.json()[ 'sid' ]

    resp = requests.get( "https://dirty.ru/api/domains/karmageddon/posts/" )

    posts = resp.json()[ 'posts' ]

    headers = { "X-Futuware-UID": uid, "X-Futuware-SID": sid }
    for post in posts :
        if ( str( post['user']['id'] ) != uid ) :
            resp = requests.post( "https://dirty.ru/api/posts/" + str( post[ 'id' ] ) + "/vote/", data = { "vote": 1 }, headers=headers )
            print( resp.text )

        resp = requests.get( "https://dirty.ru/api/posts/1289082/comments/" )
        comments = resp.json()[ 'comments' ]
        for comment in comments :
            if ( str( comment['user']['id'] ) != uid ) :
                resp = requests.post( "https://dirty.ru/api/comments/" + str( comment[ 'id' ] ) + "/vote/", data = { "vote": 1 }, headers=headers )
                print( resp.text )

if __name__ == "__main__":
    main( sys.argv )