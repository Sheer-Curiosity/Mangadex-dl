import os
import requests
import time
import urllib.request

# r1 = requests.get('https://api.mangadex.org/manga/a892e04c-e20c-4fd3-9169-d620cee8dbd4/aggregate')
#print(r1.json()['volumes']['1'])

#r2 = requests.get('https://api.mangadex.org/at-home/server/78f248e9-93b8-4fda-92d2-21f6cfc18d84')
#print(r2.json())
#img = f"{r2.json()['baseUrl']}/data/{r2.json()['chapter']['hash']}/{r2.json()['chapter']['data'][0]}"
#print(img)
#imgdown = urllib.request.urlretrieve(img, f"image1.{img[-3:]}")


print("##########################################\n\nSSMDDL: Sheer's Shitty MangaDex Downloader\n\n##########################################\n")

mangaQuery = input("Input Manga Title: ")

queryRes = requests.get(f"https://api.mangadex.org/manga?title='{mangaQuery}'&limit=100&availableTranslatedLanguage[]=en")
queryParsed = queryRes.json()

print(f"Found {queryParsed['total']} Manga Title(s)\n")


for idx, i in enumerate(queryParsed['data']):
    altTitles = []
    print(f"{idx+1}: {i['attributes']['title'].get('en')}, (Alt Title(s): ", end="")
    for j in i['attributes']['altTitles']:
        if j.get('en') is not None:
            altTitles.append(j.get('en'))
    print(*altTitles, sep=", ", end=")\n")

mangaId = None
while True:
    try:
        idChoice = int(input('Choose Manga ID To Download: '))
        assert 0 < idChoice < int(queryParsed['total'])
        mangaId = queryParsed['data'][idChoice-1]['id']
    except ValueError:
        print("Not an integer! Please enter an integer.")
    except AssertionError:
        print("Please enter an ID on the list.")
    else:
        break

chapterReq = requests.get(f"https://api.mangadex.org/manga/{mangaId}/aggregate?translatedLanguage[]=en")
chapterParsed = chapterReq.json()

chapterIds = []
chapterNums = []
chapterPageLinks = []
for i in chapterParsed['volumes']:
    volArray = []
    chapArray = []
    for j in chapterParsed['volumes'][f"{i}"]['chapters']:
        chapArray.insert(0, chapterParsed['volumes'][f"{i}"]['chapters'][f"{j}"]['chapter'])
        volArray.insert(0, chapterParsed['volumes'][f"{i}"]['chapters'][f"{j}"]['id'])
    chapterIds.insert(0, volArray)
    chapterNums.insert(0, chapArray)

finalLinks = []
for idx, i in enumerate(chapterIds):
    volLinks = []
    for idy, j in enumerate(i):
        idLinks = []
        pagesReq = requests.get(f"https://api.mangadex.org/at-home/server/{j}")
        pagesParsed = pagesReq.json()
        time.sleep(1.5)
        if pagesParsed['result'] == 'error':
            print("Rate limit exceeded, waiting for refresh...")
            time.sleep(65)
            pagesReq = requests.get(f"https://api.mangadex.org/at-home/server/{j}")
            pagesParsed = pagesReq.json()
            for k in pagesParsed['chapter']['data']:
                img = f"{pagesParsed['baseUrl']}/data/{pagesParsed['chapter']['hash']}/{k}"
                idLinks.append(img)
        else:
            for k in pagesParsed['chapter']['data']:
                img = f"{pagesParsed['baseUrl']}/data/{pagesParsed['chapter']['hash']}/{k}"
                idLinks.append(img)
        volLinks.append(idLinks)
    finalLinks.append(volLinks)

mangaName = input ("Prefix name for downloaded manga: ")

for idx, i in enumerate(finalLinks):
    volNumber = idx+1
    for idy, j in enumerate(i):
        chapterNumber = chapterNums[idx][idy]
        for idz, k in enumerate(j):
            urllib.request.urlretrieve(k, f"./Downloads/{mangaName}-volume-{volNumber}-chapter-{chapterNumber}-page-{idz+1}.{k[-3:]}")
