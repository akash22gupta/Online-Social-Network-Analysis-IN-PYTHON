This assignment was on open-ended exploration of online social networking, so I choose Twitter's data for analysis.
There are 4 parts of this assignment as explained below.


collect.py -
In this part I have collected the data (Tweets and Users) about the recently released movie "Justice League".
 I have collected all the tweets which mentioned the movie name and then clustered based on the mentions in their tweets.
  Later I classified them based on the negative and positive sentiments used in the tweets.
  I have collected all the tweets using the Twitter API's search filter. This method is based on REST API call.
  Also I have made sure that the tweets are not repeated. The number of queries made are 10 in order to collect data quickly.

cluster.py -
In this part of assignment, I worked  data collected in the collect-phase and created a communities. To detect communities I have used
 detection algorithm (girvan_newman). This approach works on the betweenness of the edge. In the process of detecting communities (or clustering)
 I have filtered out those tweets which has @ in it, then I stored the link between the user and the mentioned user in his/her tweet.
 Also, I made sure that the celebrities accounts starring in the movie are removed from these since we do not want the promotion tweets.
 After forming these links, I have created a graph and ran girvan_newman algorithm on it to create the communities.


classify.py -
In this part, I have done the sentiment analysis of the tweets using AFINN dataset.
The tweets are classified according to the scores and then classified accordingly.
classify data along twitter messages into 3 classifications, good, neutral and bad emotion.
Emotion score > 0  Positive
Emotion score = 0  Neutral
Emotion score < 0  Negative


summarize.py -
This is just to generate the statistical data of our analysis. I have generated statistical records like
  - Number of users collected:
  - Number of messages collected:
  - Number of communities discovered:
  - Average number of users per community:
  - Number of instances per class found:
  - One example from each class:
  and then saved them in summary.txt file for further reference.




  conclusion -
- In the these different phases of analysis I come to know like we need to collect the relevant data, and this is most important phase of our analysis.
  If we get wrong data our whole analysis can go wrong. So this is very important phase. also I faced many different challenges like collecting
  data for not very famous attributes cause very less data and time as well. so we need to very wise on data collection. This is most time consuming phase.
- In clustering phase similarity calculation gives better result and good formation of cluster/communities.
- We need to remove the outlier in this phase so it wont make any problem in next subsequent phases of classification
- In classify phase we have to train our model based on the available train data. We have to take care of model over fitting.
