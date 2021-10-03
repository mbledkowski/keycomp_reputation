import psycopg
import tweepy
import praw
import git

repo = git.Repo(search_parent_directories=True)

cridentials = open(".env", "r").read().splitlines()

twitter = tweepy.Client(bearer_token=cridentials[4])

reddit = praw.Reddit(
    client_id=cridentials[5],
    client_secret=cridentials[6],
    password=cridentials[7],
    user_agent="keycomp by u/mble",
    username="mble",
)

twitterProfiles = []
redditProfiles = []

authors=[]

with psycopg.connect(
  host=cridentials[0],
  port=cridentials[1],
  user=cridentials[2],
  password=cridentials[3]
) as conn:
  with conn.cursor() as cur:
    cur.execute("""
      SELECT (id, "Twitter", "Reddit")
      FROM authors
      WHERE "isReviewer" = true
    """)
    authors = cur.fetchall()

    for i in authors:
      iTwitter = i[0][1]
      iReddit = i[0][2]
      if iTwitter != None:
        twitterProfiles.append(iTwitter[21:-1])

      if iReddit != None:
        redditProfiles.append(iReddit[29:-1])

    twitterStats=[]
    redditStats=[]

    for i in twitter.get_users(usernames=twitterProfiles, user_fields=["public_metrics"]).data:
      try:
        twitterStats.append(i.public_metrics['followers_count'])
      except:
        twitterStats.append(0)

    for i in redditProfiles:
      try:
        redditStats.append(reddit.redditor(i).comment_karma)
      except:
        redditStats.append(0)

    t =0
    r = 0
    for index, i in enumerate(authors):
      iTwitter = i[0][1]
      iReddit = i[0][2]
      xNull = False
      yNull = False
      if iTwitter != None:
        x=twitterStats[t]
        t += 1
      else:
        x=-1

      if iReddit != None:
        y=redditStats[r]
        r += 1
      else:
        y=-1

      cur.execute("""
      INSERT INTO reputation(authorid,twitterFollowers, redditKarma, score, software)
      VALUES ({authorid}, {tF}, {rK}, {score}, \"{soft}\");
      """.format(authorid=i[0][0], tF="NULL" if x==-1 else x, rK="NULL" if y==-1 else y, score=((x/(x+256))+2*(y/(y+2048)))/3, soft = f"mbledkowski/keycomp_reputation {sorted(repo.tags, key=lambda t: t.commit.committed_datetime)[-1]} {repo.head.object.hexsha[0:7]}"
))