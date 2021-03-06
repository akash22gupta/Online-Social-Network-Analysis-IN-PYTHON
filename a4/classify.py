"""
classify.py
"""
import re
from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import json
import pickle

def tokenize(tweet):

    if not tweet:
        return []
    tweet = tweet.lower()
    tweet = re.sub('http\S+', ' ', tweet)
    tweet = re.sub('@\S+', '', tweet)
    tweet = re.sub('#\S+', '', tweet)
    tokens = re.sub('\W+', ' ', tweet).split()
    return tokens

def afinn_sentiment_analysis(terms, afinn):
    positives = 0
    negatives = 0
    for t in terms:
        if t in afinn:
            if afinn[t] > 0:
                positives += afinn[t]
            else:
                negatives += -1 * afinn[t]
    return positives, negatives

def classification(tokens, tweets, afinn):
    positives = []
    negatives = []
    neutral = []
    for token_list, tweet in zip(tokens, tweets):
        pos, neg = afinn_sentiment_analysis(token_list, afinn)
        if pos > neg:
            positives.append((tweet['text'], pos, neg))
        elif neg > pos:
            negatives.append((tweet['text'], pos, neg))
        else:
            neutral.append((tweet['text'], pos, neg))

    positives = sorted(positives, key=lambda x: x[1], reverse=True)
    negatives = sorted(negatives, key=lambda x: x[2], reverse=True)
    neutral = sorted(neutral, key=lambda x: x[2])
    return positives, negatives, neutral

def read_tweets(filename):
    """ reads all tweets, removes duplicates, & also prune them """
    tweets = []
    with open(filename, 'r', encoding='utf-8') as fp:
        for line in fp:
            tweets.append(line.split(" || ")[3])
    set_tweet=set(tweets)
    list_tweet=list(set_tweet)
    #tweets_list = list(set(tweets))
    return list_tweet

def download_afinn():
    afinn = dict()
    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')
    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])

    return afinn

def main():
    afinn = download_afinn()
    tweets = pickle.load(open("tweets.pkl", "rb"))
    #tweets = pickle.load(open("tweets.pkl", "rb"))
    tokens = [tokenize(tweet['text']) for tweet in tweets]
    positives, negatives, neutral = classification(tokens, tweets, afinn)

    pickle.dump(positives, open('positive_tweets.pkl', 'wb'))
    pickle.dump(negatives, open('negative_tweets.pkl', 'wb'))
    pickle.dump(neutral, open('neutral_tweets.pkl', 'wb'))


if __name__ == '__main__':
    main()
