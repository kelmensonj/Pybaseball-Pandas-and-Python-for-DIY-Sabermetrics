# Pybaseball-Pandas-and-Python-for-DIY-Sabermetrics

There are a couple dependencies for this project. On Ubuntu 21.04, I did:

```
pip3 install pybaseball
pip3 install pandas
```

You'll also need either the file in the repo called 'MLBid.csv' or a file in a similar format.

Here is a huge 2 gigabyte file I made by using pybaseball to collect the last few years of statcast data:

![alt-text](https://github.com/kelmensonj/Pybaseball-Pandas-and-Python-for-DIY-Sabermetrics/blob/master/big_baseball.gif)

If you want to look at that file directly I'm sure we could figure something out.

And here is that data transformed in order to create a few metrics invented by my brother. We used this data to create better park factors and better indicators of raw power than you might typically find on Baseball Savant:

![alt-text](https://github.com/kelmensonj/Pybaseball-Pandas-and-Python-for-DIY-Sabermetrics/blob/master/transformed.gif)

A few things this project accomplished:

* Using pybaseball, pandas, and python, web scraped all publicly available statcast data for variable years and months and assembled all the data in a database
* Added additional data, player names, to the database which only featured unique player id's
* Cleaned and reshaped the data in order to produce park factors and indications of raw power that correlate year to year better than conventional methods 

And finally, here is an extended video I made about all of this where the metric gets fully explained towards the end: https://www.youtube.com/watch?v=bdmdqhmzDyQ&t=85s


