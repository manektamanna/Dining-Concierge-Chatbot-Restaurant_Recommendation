
#Importing the relevant libraries for scraping data from the Yelp API
import requests
import json
from collections import Counter

#cuisines considered are 'Italian','American (New)','Japanese','Chinese' and 'Mexican'

url = "https://api.yelp.com/v3/businesses/search" #Check details from YELP API
api_key = "ABCD" #Insert your personal API Key
headers = {'Authorization': 'Bearer %s' % api_key}

json1 = []

#Important step as only 50 values are fetched at a time and 240 values in total per request.
# I utilised multiple accounts in order to obtain enough data to fill the dynamodb tables
#Offset can be used as checkpoints for the values obtained
params={
"limit": 50,
"location": "manhattan",
"categories": "XYZ" #Insert values from the cuisines you are considering
}
response = requests.get(url, headers=headers, params=params)
businesses = response.json()['businesses']
for i in businesses:
  json1.append(i)

#Loop to run the fetching process until you exhaust your daily limit.
#This also generated a lot of duplicates which should be removed at later stages
for _ in range(27):
  params={
"limit": 50,
"offset": 50,
"location": "manhattan",
"categories": "XYZ" #Insert values from the cuisines you are considering
}
  response = requests.get(url, headers=headers, params=params)
  businesses = response.json()['businesses']
  for i in businesses:
    json1.append(i)

#Json1 contains all values of restaurants returned with associated cuisine type

#Additional filtration step just to confirm the values returned contain the required cuisines as their category values
names  = ['Italian','American (New)','Japanese','Chinese','Mexican'] #List containing list of dictionaries
food_vals = []
for name in names:
  json2 = []
  for i in json1:    
    flag = False
    for j in range(len(i)):
      if i['categories'][j]['title']==name:  #Insert values from the cuisines you are considering to store
        flag = True
      if flag:
        json2.append(i)
        cuisine_name = json2 #cuisine name will keep changing for each iteration over the names
  food_vals.append(cuisine_name)

food_vals = [Italian, American, Japanese, Chinese, Mexican] #List containing list of dictionaries

final_data = Mexican + Italian + Japanese + Chinese + American

json_data = json.dumps(final_data)

#Create json file with all the cuisine details
with open('restaurant_details.json', 'w') as f:
  f.write(json_data)

from google.colab import files
files.download('restaurant_details.json')

