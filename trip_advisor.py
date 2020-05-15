#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import pyttsx3 
import re

driver = webdriver.Chrome('C:/Users/Murali Krishna/Downloads/chromedriver')

#####Convertig Non-ascii to ascii
def non_ascii(text):
	return "".join([(i if ord(i)<128 else " ") for i in text])

##Find integers in given string
def find_numbers(string, ints=True):
    numexp = re.compile(r'[-]?\d[\d,]*[\.]?[\d{2}]*')
    numbers = numexp.findall(string)
    numbers = [x.replace(',','') for x in numbers]
    return numbers

def hotel_data(url):
	main_url = url
	id = 5
	page_count = 0
	h3 = "na"
	while True:
		try:
			driver.get(url)
			driver.implicitly_wait(30)
			print("Waiting for readmore button")
			#read = soup.find('span', attrs={'class':'hotels-review-list-parts-ExpandableReview__cta--3U9OU'})
			#print(read)
			element = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[6]/div/div[1]/div[1]/div/div[3]/div/div[3]/div/div[3]/div[3]/div[1]/div[2]/div/div')
			driver.execute_script("arguments[0].click()", element)
			print("readmore clicked")
			#driver.implicitly_wait(20)
			pagesource = driver.page_source		
			soup = BeautifulSoup(pagesource,'html.parser')
			hotel_final_rating = soup.find('span',  attrs={'class':'hotels-hotel-review-about-with-photos-Reviews__overallRating--vElGA'}).text
			print("hotel-final-rating:",hotel_final_rating)
			main_class = soup.find('div', attrs={'class':'hotels-hotel-review-about-with-photos-GoodToKnow__container--34uyo'})
			hotel_class = str(main_class.find('div', attrs={'class':'hotels-hr-about-layout-TextItem__textitem--2JToc'})).split('span')[1]
			hotel_class = hotel_class.split('hotels')[0]
			hotel_class = "".join(find_numbers(hotel_class))
			hotel_class = int(int(hotel_class)/10)
			print("hotel-class:",hotel_class)
			hotel_style_div = main_class.find_all('div', attrs={'hotels-hr-about-layout-TextItem__textitem--2JToc'})
			print(hotel_style_div)
			if(len(hotel_style_div)==2):
				h1 = str(hotel_style_div[1].text)
				h3 = h1
			elif(len(hotel_style_div)==3):
				h1 = str(hotel_style_div[1].text)
				h2 = str(hotel_style_div[2].text)
				h3 = h1+" "+h2
			hotel_style = h3				
			print("hotel-style:",hotel_style)
			review_div = soup.find_all('div', attrs={'class':'hotels-review-list-parts-SingleReview__mainCol--2XgHm'})
			#print(len(review_div))
			for each_review in review_div:
				ov_rating = each_review.find('div', attrs = {'class':'hotels-review-list-parts-RatingLine__bubbles--1oCI4'})
				ov_rating = str(ov_rating).split("bubble_rating")
				ov_rating = "".join(find_numbers(ov_rating[1]))
				ov_rating = float(int(ov_rating)/10)
				print("user-overall-rating:",ov_rating)
				review_title = each_review.find('a', attrs = {'class':'hotels-review-list-parts-ReviewTitle__reviewTitleText--3QrTy'}).text
				print("review-title:",review_title)
				date = each_review.find('div', attrs={'class':'hotels-review-list-parts-EventDate__event_date--CRXs4'}).text
				date = str(date).split(":")
				date = date[1].strip()
				print("stay-date:",date)
				try:
					trip = each_review.find('div', attrs={'hotels-review-list-parts-TripType__trip_type--2cnp7'}).text
					trip = str(trip).split(":")
					trip = trip[1].strip()
					print("trip-type:",trip)
				except:
					trip="na"	
				review = each_review.find('q', attrs={'class':'hotels-review-list-parts-ExpandableReview__reviewText--3oMkH'}).text
				
				##############Additional rating ############
				rooms = "na"
				cleanliness = "na"
				service = "na"
				value = "na"
				location = "na"
				sleep_quality = "na"
				try:
					additional_rating_div = each_review.find('div', attrs={'class':'hotels-review-list-parts-AdditionalRatings__ratings--2usnH'})
					sub_class = additional_rating_div.find_all('div', attrs={'class':'hotels-review-list-parts-AdditionalRatings__rating--3lBgs'})
					print(sub_class)
					print(len(sub_class))
					for each_class in sub_class:
						each_class = each_class.find_all("span")
						class_name = str(each_class[2].text).strip()
						print("class-name:",class_name)
						f_rating = str(each_class[1]).split("bubble_rating")
						f_rating = "".join(find_numbers(f_rating[1]))
						f_rating = float(int(f_rating)/10)
						print(f_rating)
						if(class_name == "Rooms"):
							rooms = f_rating
						elif(class_name == "Cleanliness"):
							cleanliness = f_rating
						elif(class_name == "Service"):
							service = f_rating
						elif(class_name == "Value"):
							value = f_rating
						elif(class_name == "Location"):
							location = f_rating
						elif(class_name == "Sleep Quality"):
							sleep_quality = f_rating
						else:
							rooms = "na"
							cleanliness = "na"
							service = "na"
							value = "na"
							location = "na"
							sleep_quality = "na"
				except  Exception as e:
					print(e)
					print("Additional_rating_div not found")
				obj = {
					"hotel_url":url,
					"hotel_final_rating":hotel_final_rating,
					"user_overall rating":ov_rating,
					"hotel_class":hotel_class,
					"hotel_style":hotel_style,
					"review_summary":non_ascii(str(review_title)),
					"user_review":non_ascii(str(review)),
					"date of stay":date,
					"trip type":trip,
					"value":value,
					"location":location,
					"service":service,
					"rooms":rooms,
					"cleanliness":cleanliness,
					"sleep quality":sleep_quality
					
				}
				final_data.append(obj)
			page_count+=1
			s = main_url.split("Reviews")
			k = s[0]+"Reviews"
			l= "-or"+str(id)+s[1]
			url = k+l
			print("page-count:{},row_count:{}".format(page_count,row_count))
			print("Next page:",url)
			id = id+5					
			if(page_count==10):
				print(final_data)
				return final_data
				break
		except Exception as e:
			print(e)
			print("exception found ********************************")
			engine.say("Something went wrong please check the webpage,Exception Found") 
			engine.say("cs engineer where are you") 
			return final_data


links_list = [
	"abuja_links.csv",
	"bogota_links.csv"
]
start_time = time.time()
for each in links_list:			
	df=pd.read_csv(each)
	row_count = 0
	final_data=[]
	f_Data = []
	print(len(df))	
	engine = pyttsx3.init() 
	while row_count < len(df):
		url = df.ix[row_count,1]
		print(url)
		f = hotel_data(url)
		row_count+=1
		print("****************************Row count*****************",row_count)
		engine.say("Rowcount is"+str(row_count))
		engine.runAndWait() 
		df1 = pd.DataFrame(data=f)
		city = str(each).split("_")[0]
		df1.to_csv(str(city)+"_reviews.csv",index = True)
		#with open('trip_adv_mumbai_reviews.json', 'w') as fw:
		#	json.dump(f, fw, indent=4)
print("--- %s seconds ---" % (time.time() - start_time))