import os, sys, time, collections

sys.path.append("tweepy")
import tweepy

from settings import *
api = None
handled_matches = []
record = collections.defaultdict(lambda: {"won": 0, "lost": 0})
team_number = None

matches_known = False
match_event = None
match_list = None


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
    "'login' to twitter... aka recover the access_token so that we can tweet"
    global api, team_number
    with file(".tokens", "r") as f:
        key = f.readline()
        secret = f.readline()
        team_number = f.readline()

    auth = tweepy.OAuthHandler(key, secret)
    api = tweepy.API(auth)

def parse_match(text, team_number):
    """
    Parse the text of the frcfms tweet then, begin doing some processing
    based off of the current team number. Figure out our alliance color
    and partners, whether we won or lost and update our record.
    """
    tokens = text.split(" ")
    match = {"event": tokens[0], "type": tokens[2],
             "number": int(tokens[4]),
             "teams": tokens[10:13] + tokens[14:17],
             "id": (tokens[0], tokens[2], tokens[4]), "raw": text,
             
             "red score": tokens[6], "blue score": tokens[8],
             "red alliance": tokens[10:13], "blue alliance": tokens[14:17],
             "red bonus": tokens[18], "blue bonus": tokens[20],
             "red penalty": tokens[22], "blue penalty": tokens[24],
             
             "team number": team_number}

    match["full type"] = {"P": "practice",
                          "Q": "qualification",
                          "E": "elimination"}[match["type"]]
    match["alliance"] = {True: "red",
                         False: "blue"}[team_number in match["red alliance"]]
    match["other"] = {True: "blue",
                      False: "red"}[team_number in match["red alliance"]]
    match["other teams"] = " and ".join([team for team in
                                           match[match["alliance"]+" alliance"]
                                             if team != team_number])
    match["outcome"] = {True: "won",
                        False: "lost"}[int(match[match["alliance"]+" score"]) \
                                           > int(match[match["other"]+" score"])]
    match["scores"] = "%s to %s"%(match[match["alliance"]+" score"],
                                  match[match["other"]+" score"])

    if team_number in match["teams"] and match["type"] != "P":
        record[match["event"]][match["outcome"]] += 1
    match["record"] = "(%(won)s-%(lost)s)"%(record[match["event"]])
    
    return match

def post_update(text):
    "Post a status update on twitter and print"
    print text
    if not(debug):
        api.update_status(text)

def handle_match(match):
    """
    If a match involves us, tweet the results.
    Otherwise, alert that our match is coming up 2 matches before.
    """
    if team_number in match["teams"]:
        post_update(results_template%match)
    if matches_known:
        if (match_event == match["event"]) and (match["type"] == "Q") \
                and (match["number"] in [i - 3 for i in match_list]):
            # Alerts two matches in advance, because when we get
            #     the tweet the match is done.
            post_update(alert_template%{"time": alert_time,
                                        "team number": team_number,
                                        "event": match_event})

def check_matches():
    "Check match numbers and update them"
    global matches_known, match_list, match_event
    if os.path.exists("matches.txt"):
        with file("matches.txt", "r") as f:
            match_event = f.readline().strip(" \n\t")
            match_list = [int(num) for num in f.readline().split(", ")]
            matches_known = True

def main():
    if isSetup(): login()
    else: setup()

    print "Ready"
    while True:
        if not(matches_known):
            check_matches()
            print match_event, match_list, matches_known
        
        tweets = [i for i in tweepy.Cursor(api.user_timeline, id="frcfms").items(num_tweets)]
        tweets.reverse()
        for tweet in tweets:
            match = parse_match(tweet.text, team_number)
            if match["id"] not in handled_matches:
                handle_match(match)
                handled_matches.append(match["id"])

        if debug:
            exit()
        time.sleep(90)

if __name__ == "__main__":
    main()
