
import requests

session = requests.Session()

res = session.get('https://api.covid19india.org/v4/data.json')
info = res.json()
maxState = ""
maxPerc = 0

for state in info.keys():
    curr = 100*(info[state]['total']['confirmed'] /
                info[state]['meta']['population'])
    if maxPerc < curr:
        maxPerc = curr
        maxState = state

print(maxState, max)
