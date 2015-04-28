#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient.discovery import build
from apiclient.errors import HttpError

import random
import time
import json
import httplib
import urllib2
import redis

#   https://cloud.google.com/console
#   https://console.developers.google.com/project/elite-ethos-90314/apiui/credential
#   https://developers.google.com/youtube/v3/code_samples/python#search_by_topic

DEVELOPER_KEY = "AIzaSyCTx9JLdkMHi8jCOS4W3e92MmiX0-EYFEM"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
URL = "https://www.googleapis.com/youtube/v3/videos?id={0}&key=AIzaSyCTx9JLdkMHi8jCOS4W3e92MmiX0-EYFEM%20&part=snippet,contentDetails,statistics,status"

curl https://www.googleapis.com/urlshortener/v1/url&key=AIzaSyCTx9JLdkMHi8jCOS4W3e92MmiX0-EYFEM -H 'Content-Type: application/json' -d '{"longUrl": "http://www.google.com/"}'

HEADER = {
      'cache-control': 'cache',
      'accept-encoding': 'gzip,deflate,sdch',
      'accept': 'application/json; charset=utf-8',
      'accept-language': 'es,en-US;q=0.8,en;q=0.6',
      'user-agent': "Mozilla/5.0 (X11; Linux x86_64)",
      'connection': 'keep-alive', 
      'DNT': "1" }

def goo_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyCTx9JLdkMHi8jCOS4W3e92MmiX0-EYFEM'
    postdata = {'longUrl':url}
    headers = {'Content-Type':'application/json'}
    req = urllib2.Request(
        post_url,
        json.dumps(postdata),
        headers
    )
    ret = urllib2.urlopen(req).read()
    print ret
    return json.loads(ret)['id']


def GET(_id):
  req = urllib2.Request(URL.format(_id))
  for k, v in HEADER.iteritems():
    req.add_header(k, v)
  resp = urllib2.urlopen(req)
  content = json.loads(resp.read())
  return content

def statistics(sta):
  viewCount = int(sta["viewCount"])
  likeCount = int(sta["likeCount"])
  dislikeCount = int(sta["dislikeCount"])
  favoriteCount = int(sta["favoriteCount"])
  commentCount = int(sta["commentCount"])
  result = sum([commentCount, favoriteCount, dislikeCount, likeCount, viewCount])
  promedio = result/5
  pdigits, rdigits = len(str(promedio)), len(str(result))
  if pdigits == rdigits:
    return True
  else:
    return None

def shuffle(array):
  random.shuffle(array)
  pos = len(array)-2
  return array[pos]

def youtube_search(**params):
  # https://developers.google.com/youtube/v3/docs/search/list

  keywords = params.get("keywords")
  maxsearch = params.get("maxsearch")
  typeorder = params.get("order")

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  result = youtube.search().list(
    q=keywords,
    part="id,snippet",
    order=typeorder,
    maxResults=maxsearch
  ).execute()

  return result

listorders = ["date", "rating", "relevance", "videoCount", "viewCount", "title"]
animalskeywords = ["dog", "cat", "horser", "duck", "squirrel", "pig"]
magiclist = ["{0} funny", "{0} attractive", "{0} bad", "{0} ugly", "{0} baddly"]
#vehiculekeywords = ['cars', 'truck', 'bicleta', 'motocicley']
# inspired, odio, amor, y cosas asi (terminos que generen estos sentimientos), humor primero
    
if __name__ == "__main__":
    for term in magiclist:
      for key in animalskeywords:
        keyword = term.format(key)
        try:
          search_response = youtube_search(keywords=keyword, maxsearch=50, orders="viewCount")
        except HttpError, e:
          print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        else:
          for search_result in search_response.get("items", []):
              #videos.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
              print search_result["snippet"]["title"]
              print search_result["id"]["videoId"]
              result = GET(search_result["id"]["videoId"])
              condition = statistics(result["items"][0]["statistics"])
              if condition:
                print result
                #envio el link del video a redis
              else:
                continue