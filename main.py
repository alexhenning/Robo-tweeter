import os, sys, time, getpass, collections

sys.path.append("tweepy")
import tweepy

api = None
handled_matches = []
record = collections.defaultdict(lambda: {"won": 0, "lost": 0})
team_number = None
template = "In match number %(match number)s team %(team number)s was on the %(alliance)s with teams %(other teams) and %(outcome)s %(scores)s. %(record)s"

consumer_key = "r4FqKGKt9Uh9kwh6STEUQ"
consumer_secret = "1Z5ey0jVy86PHUCyy8hLgs3WHVSEpnDxhH4zN73XfE"

def isSetup():
    "Check if robo-tweeter is setup"
    return os.path.exists(".tokens")

def setup():
    "Run the setup process to initializing robo-tweeter"
    global api
    print "Setting up robo-tweeter..."
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'

    print "Please visit `%s' to enable this application.\nPlease enter the verifier code from twiter"%(redirect_url,)
    verifier = raw_input("Verifier: ")

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'

    api = tweepy.API(auth)
    print "Authenticated!"

    # Save login
    with file(".tokens", "w") as f:
        f.write("%s\n%s\n%s"%(auth.access_token.key,
                              auth.access_token.secret,
                              raw_input("Team number: ")))
    

def login():
    "'login' to twitter... aka recover the access_token"
    global api, team_number
    with file(".tokens", "r") as f:
        key = f.readline()
        secret = f.readline()
        team_number = f.readline()

    auth = tweepy.OAuthHandler(key, secret)
    api = tweepy.API(auth)

def parse_match(text, team_number):
    tokens = text.split(" ")
    match = {"event": tokens[0], "match type": tokens[2], "match number": tokens[4],
             "red score": tokens[6], "blue score": tokens[8],
             "red alliance": tokens[10:13], "blue alliance": tokens[14:17],
            "teams": tokens[10:13] + tokens[14:17],
             "red bonus": tokens[18], "blue bonus": tokens[20],
             "red penalty": tokens[22], "blue penalty": tokens[24],
             
             "id": (tokens[0], tokens[2], tokens[4]), "raw": text,
             "team number": team_number}
    
    match["alliance"] = {True: "red",
                         False: "blue"}[team_number in match["red alliance"]]
    match["other"] = {True: "blue",
                      False: "red"}[team_number in match["red alliance"]]
    match["other teams"] = "and".join([team for team in
                                         match[match["alliance"]+" alliance"]
                                           if team != team_number])
    match["outcome"] = {True: "won",
                        False: "lost"}[int(match[match["alliance"]+" score"]) \
                                           > int(match[match["other"]+" score"])]
    match["scores"] = "%s to %s"%(match[match["alliance"]+" score"],
                                  match[match["other"]+" score"])

    record[match["event"]][match["outcome"]] += 1
    match["record"] = "(%(won)s-%(lost)s-0)"%(record[match["event"]])
    
    return match

def handle_match(match, template=template):
    if team_number in match["teams"]:
        print template%match
        # api.update_status("Playing with tweepy.")

def main():
    if isSetup(): login()
    else: setup()

    print "Ready"
    while True:
        for tweet in tweepy.Cursor(api.user_timeline, id="frcfms").items(20):
            match = parse_match(tweet.text, team_number)
            if match["id"] not in handled_matches:
                handle_match(match)
                handled_matches.append(match["id"])
                
        time.sleep(90)

if __name__ == "__main__":
    main()
