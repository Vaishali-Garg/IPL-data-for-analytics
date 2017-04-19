#!/usr/bin/env python

import sys, yaml, csv, glob, attr

def usage():
    print("Usage: ipl.py <yaml-files-dir>")
    sys.exit(1)

curr_match_id = 0
def generate_match_id():
    global curr_match_id
    curr_match_id += 1
    return curr_match_id

@attr.s
class Match(object):
    id = attr.ib( default=attr.Factory(generate_match_id))
    season = attr.ib( default="")
    city = attr.ib( default="")
    date = attr.ib( default="")
    team1 = attr.ib( default="")
    team2 = attr.ib( default="")
    toss_winner = attr.ib( default="")
    toss_decision = attr.ib( default="")
    result = attr.ib( default="normal")
    dl_applied = attr.ib( default=0)
    winner = attr.ib( default="")
    win_by_runs = attr.ib( default=0)
    win_by_wickets = attr.ib( default=0)
    player_of_match = attr.ib( default="")
    venue = attr.ib( default="")
    umpire1 = attr.ib( default="")
    umpire2 = attr.ib( default="")
    umpire3 = attr.ib( default="")

    @staticmethod
    def columns():
        return ["id", "season", "city", "date", "team1", "team2", "toss_winner",
                "toss_decision", "result", "dl_applied", "winner",
                "win_by_runs", "win_by_wickets", "player_of_match", "venue",
                "umpire1", "umpire2", "umpire3"]

    def values( self):
        return [self.id, self.season, self.city, self.date, self.team1, self.team2,
                self.toss_winner, self.toss_decision, self.result,
                self.dl_applied, self.winner, self.win_by_runs,
                self.win_by_wickets, self.player_of_match, self.venue,
                self.umpire1, self.umpire2, self.umpire3]

@attr.s
class Delivery(object):
    match_id = attr.ib()
    inning = attr.ib()
    batting_team = attr.ib()
    bowling_team = attr.ib()
    over = attr.ib()
    ball = attr.ib()
    batsman = attr.ib()
    non_striker = attr.ib()
    bowler = attr.ib()
    is_super_over = attr.ib( default=0)
    wide_runs = attr.ib( default=0)
    bye_runs = attr.ib( default=0)
    legbye_runs = attr.ib( default=0)
    noball_runs = attr.ib( default=0)
    penalty_runs= attr.ib( default=0)
    batsman_runs = attr.ib( default=0)
    extra_runs = attr.ib( default=0)
    total_runs = attr.ib( default=0)
    player_dismissed = attr.ib( default="")
    dismissal_kind = attr.ib( default="")
    fielder = attr.ib( default="")

    @staticmethod
    def columns():
        return ["match_id", "inning", "batting_team", "bowling_team", "over",
                "ball", "batsman", "non_striker", "bowler", "is_super_over",
                "wide_runs", "bye_runs", "legbye_runs", "noball_runs",
                "penalty_runs", "batsman_runs", "extra_runs", "total_runs",
                "player_dismissed", "dismissal_kind", "fielder"]

    def values( self):
        return [self.match_id, self.inning, self.batting_team,
                self.bowling_team, self.over, self.ball, self.batsman,
                self.non_striker, self.bowler, self.is_super_over,
                self.wide_runs, self.bye_runs, self.legbye_runs,
                self.noball_runs, self.penalty_runs, self.batsman_runs,
                self.extra_runs, self.total_runs, self.player_dismissed,
                self.dismissal_kind, self.fielder]

def write_match_info( match_data, match, matches_f):
    info = match_data["info"]
    if "city" in info:
        match.city = info["city"]
    elif info["venue"] == "Sharjah Cricket Stadium":
        match.city = "Sharjah"

    match.date = info["dates"][0]
    match.season = match.date.year

    if "winner" in info["outcome"]:
        match.winner = info["outcome"]["winner"]
    elif "eliminator" in info["outcome"]:
        match.winner = info["outcome"]["eliminator"]

    if "method" in info["outcome"] and info["outcome"]["method"] == "D/L":
        match.dl_applied = 1

    if "result" in info["outcome"]:
        match.result = info["outcome"]["result"]
    else:
        if "runs" in info["outcome"]["by"]:
            match.win_by_runs = info["outcome"]["by"]["runs"]
        else:
            match.win_by_wickets = info["outcome"]["by"]["wickets"]

    if "player_of_match" in info:
        match.player_of_match = info["player_of_match"][0]

    match.team1 = match_data["innings"][0]["1st innings"]["team"]
    if info["teams"][0] == match.team1:
        match.team2 = info["teams"][1]
    else:
        match.team2 = info["teams"][0]
    match.toss_winner = info["toss"]["winner"]
    match.toss_decision = info["toss"]["decision"]
    match.venue = info["venue"]
    match.umpire1 = info["umpires"][0]
    match.umpire2 = info["umpires"][1]
    if len(info["umpires"]) > 2:
        match.umpire3 = info["umpires"][2]

    matches_f.writerow(match.values())

def write_deliveries_info( match_data, match, deliveries_f):
    inning_number = 0
    for inning in match_data["innings"]:
        inning = list(inning.values())[0]

        inning_number += 1
        if inning_number == 1:
            inning_name = "Inning 1"
            is_super_over = 0
        elif inning_number == 2:
            inning_name = "Inning 2"
            is_super_over = 0
        elif inning_number == 3:
            inning_name = "Super Over 1"
            is_super_over = 1
        elif inning_number == 4: 
            inning_name = "Super Over 2"
            is_super_over = 1
        else: 
            print("Bad inning number.")
            sys.exit(1)

        batting_team = inning["team"]
        if match.team1 == batting_team:
            bowling_team = match.team2
        else:
            bowling_team = match.team1

        for d_data in inning["deliveries"]:
            over_ball = str(list(d_data.keys())[0])
            over = int(over_ball.split('.')[0]) + 1
            ball = int(over_ball.split('.')[1])
            d_data = list(d_data.values())[0]

            d = Delivery(match_id=match.id, inning=inning_number,
                    batting_team=batting_team, bowling_team=bowling_team,
                    over=over, ball=ball, batsman=d_data["batsman"],
                    non_striker=d_data["non_striker"], bowler=d_data["bowler"],
                    is_super_over=is_super_over,
                    wide_runs=d_data.get("extras", {}).get("wides", 0),
                    bye_runs=d_data.get("extras", {}).get("byes", 0),
                    legbye_runs=d_data.get( "extras", {}).get( "legbyes", 0),
                    noball_runs=d_data.get( "extras", {}).get( "noballs", 0),
                    penalty_runs=d_data.get( "extras", {}).get( "penalty", 0),
                    batsman_runs=d_data["runs"]["batsman"],
                    extra_runs=d_data["runs"]["extras"],
                    total_runs=d_data["runs"]["total"], 
                    player_dismissed=d_data.get( "wicket", {}).get( "player_out", ""),
                    dismissal_kind = d_data.get( "wicket", {}).get( "kind", ""),
                    fielder = d_data.get( "wicket", {}).get( "fielders", [""])[0])

            deliveries_f.writerow( d.values())

def process( match_data_f, matches_f, deliveries_f):
    match_data = yaml.load( match_data_f)
    if match_data["meta"]["data_version"] != 0.7:
        print( "Unsupported version: %s" % str(match_data["meta"]["version"]))
        sys.exit(1)

    match = Match()
    write_match_info( match_data, match, matches_f)
    write_deliveries_info( match_data, match, deliveries_f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    with open( "matches.csv", "w") as matches_f:
        matches_f = csv.writer( matches_f)
        matches_f.writerow( Match.columns())
        with open( "deliveries.csv", "w") as deliveries_f:
            deliveries_f = csv.writer( deliveries_f)
            deliveries_f.writerow( Delivery.columns())
            for fpath in glob.glob(sys.argv[1] + "/*.yaml"):
                print(fpath)
                with open( fpath, "r") as match_data_f:
                    process( match_data_f, matches_f, deliveries_f)
