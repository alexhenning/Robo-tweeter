
# Template tweet for the results of a match
results_template = "In %(match type)s match number %(number)s team %(team number)s was on the %(alliance)s alliance with teams %(other teams)s and %(outcome)s %(scores)s. %(record)s #FRC%(team number)s %(event)s"

# Template tweets for an upcoming match
alert_template = "Team %(team number)s will be up in about %(time)s minutes. #FRC%(team number)s %(event)s"

# Time to alert when warning of an upcoming match.
# It's used sent out after seeing the score for a match three matches before
#     your next match which leaves two matches to run before yours. Default: 15
#     assuming 7.5 from start to start.
alert_time = 15

# When in debug mode, the code runs once and prints the results. Normally
#     it runs checking every minute and a half. It also doesn't tweet while
#     debugging. Should normally be false.
debug = True
num_tweets = {True: 1000, False: 20}[debug]
