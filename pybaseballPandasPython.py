from pybaseball import statcast
import pandas
import math
import csv
from functools import reduce

#This was one of my first projects. Not one function in here, so execution is straightforward
#######
#you can download pybaseball on github. It scrapes websites like baseballreference.com and returns statcast data in very neat csv files. Great work 
#that is still being updated. All the other imports are pretty standard and if you don't have them downloaded google will help you
#######

list_months = ['03','04','05','06','07','08','09','10','11','12']  
list_years = ['15','16','17','18','19']
#######
#list_months and list_years tell what data to download. It's broken up into chunks because if you tell pybaseball to download everything at once,
#there is almost always an error message. If you want just May 2018, delete from list_months everything besides '05' and delete from list_years
#everything besides '18'
#######

list_dfs = []

for year in list_years:
	for month in list_months[0:-1]:
		start = '20' + year + '-' + month + '-01'
		end = '20' + year + '-' + list_months[list_months.index(month) + 1] + '-01'
		data = statcast(start_dt = start, end_dt = end)
		list_dfs.append(data)
		
#######
#Lines 21-26 iterate over list_years and list_months and call the function statcast from pybaseball in order to generate a 
#list of pandas dataframes stored within list_dfs
#######

finalDf = pandas.concat(list_dfs)
finalDf = finalDf.drop_duplicates()
finalDf.to_csv('pybaseballVidCSV.csv') #############This line here is the last important line if you just want all the data in a csv

#######
#Lines 33-35 concatenate and store all the downloaded statcast data into the csv file pybaseballVidCSV.csv
#######

################################################################################

batterStatcast = pandas.read_csv("pybaseballVidCSV.csv") 
batterStatcast = batterStatcast[['batter','game_date','launch_speed','launch_angle', 'description']]
batterStatcast = batterStatcast.dropna()
batterStatcast = batterStatcast[batterStatcast['description'].str.contains('hit_into_play')]
batterStatcast = batterStatcast.drop_duplicates()
noBunts = batterStatcast[batterStatcast.launch_speed >= 45]

#######
#Lines 43-45 store in the dataframe 'noBunts' statcast data filtered out based on column name, whether or not the substring 'hit_into_play' is in the 
#'description' column, and whether or not the launch_speed column entry is greater than or equal to 45. Again, google can help here, you can narrow down 
#your dataframe to whatever you want using pandas
#######

def getYear(my_list, position):
	return my_list[position]
	
######
#The getYear function will return an entry in a list.
######
	
noBunts.loc[:, 'game_date'] = noBunts.game_date.str.split('-').apply(getYear, position = 0)

######
#Line 63 updates the noBunts dataframe column 'game_date' by overwriting the full date with the year alone
######

noBunts['percFive'] = ''
noBunts['percTen'] = ''

######
#Line 69-70 just create empty columns in the dataframe
######

#################################################################################

avgSpeed = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_speed.mean().reset_index()) 
avgSpeed.rename(columns={'launch_speed' : 'Avg Exit Velo'}, inplace = True)

avgAngle = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_angle.mean().reset_index())
avgAngle.rename(columns={'launch_angle' : 'Avg Launch Angle'}, inplace = True)

battedBalls = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_speed.count().reset_index())
battedBalls.rename(columns={'launch_speed' : 'Batted Balls'}, inplace = True)

stdSpeed = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_speed.std().reset_index())
stdSpeed.rename(columns={'launch_speed' : 'Std Exit Velo'}, inplace = True)

stdAngle = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_angle.std().reset_index())
stdAngle.rename(columns={'launch_angle' : 'Std Launch Angle'}, inplace = True)

############################################################################

#######
#Lines 78-91 all create groupby objects based on various criteria. 
#######

batterYr_grp = noBunts.groupby(['batter', 'game_date']) #a groupby object by batter and year

batters = noBunts.batter.unique() #list of unique batters in the originals dataframe
years = noBunts.game_date.unique() #list of unqiue years in the oriignal dataframe

for player in batters:
	for year in years: #for each batter, there are up to 4 or 5 years. some have only one year, hence the try and except
		try:
			x = batterYr_grp.get_group((player, year)) #getting a specific player in a specific year
			q5 = x.launch_speed.quantile(.95) #getting 95th percentile of launch_speed
			q10 = x.launch_speed.quantile(.90)
			avgQ5 = x[x.launch_speed >= q5].launch_speed.mean() #getting the average of the top 5% launch_speed events
			avgQ10 = x[x.launch_speed >= q10].launch_speed.mean()
			noBunts['percFive'].loc[(noBunts['batter'] == player) & (noBunts['game_date'] == year)] = avgQ5 #adding this statistic to the noBunts dataframe
			noBunts['percTen'].loc[(noBunts['batter'] == player) & (noBunts['game_date'] == year)] = avgQ10
#The statistics added here correlate and stabilize better than looking at average exit velocity alone. Average of Top 10% Exit Velocity Events is therefore a good indicator of raw power
		except: #credit to my brother for coming up with the stat. He's a baseball genius and he devised the statistical methods in this project
			pass
			
#####
#Lines 99-116 are all about the pandas function 'get_group'. This is used to look at launch speed events for individual players for individual years,
#and is then used to fill out the columns created in lines 69-70. 
#####

xyz = noBunts[['batter', 'game_date', 'percFive', 'percTen']]
xyz.rename(columns = {'percFive' : 'Avg Top 5%', 'percTen' : 'Avg Top 10%'}) #A clean look at the new statistics

medSpeed = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_speed.median().reset_index())
medSpeed.rename(columns={'launch_speed' : 'Med Exit Velo'}, inplace = True) #here we want a look at the median launch speed for each player and year, to compare with the new stats

medAngle = pandas.DataFrame(noBunts.groupby(['batter', 'game_date']).launch_angle.median().reset_index())
medAngle.rename(columns={'launch_angle' : 'Med Launch Angle'}, inplace = True) #here we're getting the median launch angle

dfs = [avgSpeed, avgAngle, battedBalls, stdSpeed, stdAngle, medSpeed, medAngle, xyz]
finalDf = reduce(lambda left,right: pandas.merge(left, right, on=['batter', 'game_date'], how='left'), dfs) #putting it all together in a dataframe. One of the reasons i dont like pandas

idCSV = pandas.read_csv("mlbamID.csv") #check my repo for this file, otherwise you can find a similar file online. It's playerID's and names according to MLBAM
#####
#idCSV is a csv file I downloaded online. I don't know exactly where I got it, but it's a file containing MLB player names as well
#as their unique MLBAM id. MLBAM id's are used without player names in order to differentiate between unique MLB players. idCSV will be used to simply
#add player names to the noBunts dataframe, but is unneccessary in the data analysis process unless you need the player name. 
#####
nameID = idCSV[['MLBID', 'MLBNAME']]


					     ^^^^^^###########IMPORTANT########^^^^^

finalDf = reduce(lambda left,right: pandas.merge(left, right, left_on=['batter'], right_on=['MLBID'], how='left'), [finalDf, nameID]) #again, bad, complex syntax
del finalDf['MLBID']
finalDf.rename(columns={'batter' : 'PlayerID', 'game_date' : 'Year', 'MLBNAME' : 'Player Name'}, inplace = True)
finalDf = finalDf.drop_duplicates()
finalDf.to_csv('pybaseballVidCSV2.csv') #this csv has the data organized by player and year with my brother's new stats

############################################################################

df = pandas.read_csv('pybaseballVidCSV.csv') #now we're reading the csv back in in order to get park factors
df = df[['home_team','game_year','hit_distance_sc','events','game_date','hc_x','hc_y','launch_speed','launch_angle','batter']] 
df = df.dropna()
df = df.loc[df['hit_distance_sc'] > 250] #limiting dataframe to hits that went far
df['launch_direction'] = df.apply(lambda x: 0 if x['hc_x'] == 125.42 else (math.degrees(math.atan((x['hc_x']-125.42)/(198.27-x['hc_y'])))), axis=1)
#this line above is a trigonometric formula in order to estimate hit distance, because statcast releases final position vectors which are different
def labelHomer(string):
	if string == 'home_run': #hey a really complex function
		return 1
	else:
		return 0 #this is just being used to create a label column for home runs

def field(number):
	for i in range(-45,45,1): #a function that categorizes the launch_angles into 90 intervals
		if number <= i:
			return i

df['Field'] = df['launch_direction'].apply(field)
df['events'] = df['events'].apply(labelHomer)

directions = df['Field'].unique() #all the launch angle intervals
years = df['game_year'].unique() #all the years
venues = df['home_team'].unique() #all the ballparks

LISTDFS = []

for year in years:
	for venue in venues:
		for direction in directions:
			dfTemp = df.loc[(df.game_year==year) & (df.home_team==venue) & (df.Field==direction)] 
			LISTDFS.append(dfTemp) #here we're just reordering the dataframe based on years, venue, and launch_angle

finalDF = pandas.concat(LISTDFS)
finalDF = finalDF.rename(columns= {'home_team':'Home_Team','game_year':'Year','hit_distance_sc':'Distance','events':'Bop','launch_direction':'Launch_Direction','game_date':'Date'}).reset_index()
del finalDF['index']

for year in years:
	partDF = finalDF.loc[finalDF['Year'] == year]
	partDF.to_csv(str(int(year)) + 'launch_direction1deg_names.csv') #now for each year we get a csv with launch direction, home run label, and venue
	
########################################################################

list_files = ['2015launch_direction1deg.csv','2016launch_direction1deg.csv','2017launch_direction1deg.csv','2018launch_direction1deg.csv','2019launch_direction1deg.csv']

LIST_DF = []

for csv in list_files:
	df = pandas.read_csv(csv)
	LIST_DF.append(df)
	
year = 2015

for df in LIST_DF:
	global year
	rowsData = []
	
	grps = df.groupby(['Home_Team','Bop', 'Field']) #another groupby object, this will allow the use of get_group below
	venues = df.Home_Team.unique()
	fields = df.Field.unique()
	for venue in venues:
		for field in fields:
			try:
				homeruns = grps.get_group((venue, 1, field)) #getting all the home run batted ball events for that year, venue, and launch direction
				q5 = homeruns.Distance.quantile(.05) #getting the shortest homeruns for this group
				minimum = homeruns.Distance.min() #getting the single shortest home run
			except:
				q5 = 'na' #sometimes nobody hit a home run at a particular angle
				minimum = 'na'
			try:
				not_homeruns = grps.get_group((venue, 0, field)) #getting all near homeruns for that year, venue, and launch direction
				q95 = not_homeruns.Distance.quantile(.95) #getting the longest near home runs for this group
				maximum = not_homeruns.Distance.max() #getting the longest near home run
			except:
				q95 = 'na' #again, some missing data handled with try and except
				maximum = 'na'
			rowData = [venue,field,minimum,q5,maximum,q95] #now we create a row of data, the ballpark, angle, min homer, 5th percentile homerun distance, max flyball, 95th percentile flyball distance
			rowsData.append(rowData)

	deg_DF = pandas.DataFrame(rowsData,columns = ['Home_Team','Deg_Increment','Min_HR','5%_HR','Max_FB','95%_FB'])
	deg_DF.to_csv(str(year)+'parkFactors.csv') #now, you will get csv files so you can estimate how far a ball must be hit in each ballpark in each year to get a homerun
	year+=1 #you can adjust your projections based on where a hitter hits the ball, instead of just what ballpark they'll be playing in
	
dfMapper = pandas.read_csv('pybaseballVidCSV2.csv')

years = ['2015','2016','2017','2018','2019']

for year in years:
	df = pandas.read_csv(year + 'launch_direction1deg_names.csv')
	finalDf = reduce(lambda left,right: pandas.merge(left, right, left_on=['batter'], right_on=['PlayerID'], how='left'), [df,dfMapper])
	finalDf = finalDf[['PlayerID', 'Player Name', 'Home_Team','Year_x','Distance','Bop','Date','hc_x','hc_y','launch_speed','launch_angle','Launch_Direction','Field']]
	finalDf = finalDf.drop_duplicates()
	finalDf.to_csv(str(year) + 'parkfactorData.csv')




