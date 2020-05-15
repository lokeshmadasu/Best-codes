import json
import urllib
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import re



def non_ascii(text):
    return ''.join([(i if ord(i) < 128 else ' ') for i in text])

def find_numbers(string, ints=True):
    numexp = re.compile(r'[-]?\d[\d,]*[\.]?[\d{2}]*')
    numbers = numexp.findall(string)
    numbers = [x.replace(',','') for x in numbers]
    return numbers

def amz_prod_review(url,temp,soup3):
    review_data = ""
    dict={}
    retrieval_count=1
    while True:
        try:
            print "prod_review enters"
            source=requests.get(url).content
            soup3 = BeautifulSoup(source, "html.parser")
            print "Page_source"
            reviews_div = soup3.find("div", attrs={'class': 'a-section a-spacing-none review-views celwidget'})
            #print reviews_div
            sub = reviews_div.find_all("div", attrs={'class': 'a-section review'})
            for i in sub:
                print "1"
                title_div=i.find_all("div",attrs={'class':'a-row'})
                print "2"
                title = title_div[0].find_all("a")
                title = str(non_ascii(title[1].text))
                review_data = str(non_ascii(i.find("div", attrs={'class': 'a-row review-data'}).text))
                dict["user_" + str(temp)] = title + "," + review_data
                #print title, review_data
                temp = temp + 1
            #print dict
            return [dict,temp,soup3]
            break
        except AttributeError:
                print "################# Source error#######"
                title = soup3.find("title").text
                print title#Robot Check#503 - Service Unavailable Error
                if retrieval_count<=5:
                    time.sleep(3)
                else:
                    return dict,temp
                    break
                retrieval_count=retrieval_count+1


def amz_prod_page(url):
    print url
    final_dict={}
    amazon={}
    soup3=""
    review ={}
    id =1
    temp = 1
    retrieval_count=1
    max_retries_count =1
    amz_rating={}
    final_dict["amazon_url"] = url
    main_url = url
    url = str(main_url)
    substr1 = "dp"
    substr2 = "product-reviews"
    review_url = url.replace(substr1, substr2)
    while True:
            try:
                print id
                url = review_url + "/ref=cm_cr_getr_d_paging_btm_next_" + str(id) + "?ie=UTF8&reviewerType=all_reviews&pageNumber=" + str(id)
                if id==1:
                    ###############rating_division###########################################
                    az=requests.get(url).content
                    az_source = BeautifulSoup(az,"html.parser")
                    total_div = az_source.find_all("div",attrs={'class':'a-fixed-left-grid-col a-col-right'})
                    total_count = int(str(total_div[0].text).replace(",",""))
                    rating_div = az_source.find("table",attrs={'class':'a-normal a-align-middle a-spacing-base'})
                    for i in rating_div.find_all("tr"):
                            key= str(non_ascii(i.find_all("td")[0].text)).replace("u","")[0:6]
                            value = find_numbers(str(non_ascii(i.find_all("td")[2].text)).replace("u",""))
                            percentage_value=int(value[0])
                            value=int(round((percentage_value/100.0)*total_count))
                            amz_rating[key] = value
                    print amz_rating
                    amazon["rating_count"]=amz_rating
                    #############################rating_division ends##########################
                    data= amz_prod_review(url,temp,soup3)
                    review = data[0]
                    temp = data[1]
                    soup3 = data[2]
                    print review
                    amazon["review"] =review
                    id=id+1
                elif id==490:
                    print "60 pages done"
                    amazon["review"] = review
                    final_dict["amazon"] = amazon
                    return final_dict
                    break
                else:
                    print "getting"
                    try:
                        print "this is try block"
                        print url
                        data = amz_prod_review(url,temp,soup3)
                        temp =data[1]
                        soup3 = data[2]
                        review.update(data[0])
                        print review
                        next_div = soup3.find("li", attrs={'class': 'a-last'})
                        #print next_div
                        sub = next_div.find_all("a")
                        print sub[0].text
                        id=id+1
                    except IndexError:
                        print review
                        print "Exception block"
                        amazon["review"]=review
                        final_dict["amazon"]=amazon
                        return final_dict
                        break
                    except (requests.exceptions.ConnectionError, IndexError) as e:
                        print "Max retries"
                        pass
            except AttributeError:
                if retrieval_count<=5:
                    time.sleep(3)
                else:
                    amazon["review"]={}
                    amazon["rating_count"]={}
                    final_dict["amazon"]=amazon
                    return final_dict
                    break
                retrieval_count = retrieval_count + 1
            except (requests.exceptions.ConnectionError, IndexError) as e:
                print "Max retries"
                if max_retries_count==4:
                    amazon["review"] = {}
                    amazon["rating_count"] = {}
                    final_dict["amazon"] = amazon
                    return final_dict
                    break
                else:
                    pass
                max_retries_count=max_retries_count+1
################################################################################################

url ="https://www.amazon.in/Moto-Plus-32GB-Fine-Gold/dp/B071ZZ8N5Y"
df = pd.read_csv('Book2.csv')
print len(df)
#temp =1
all_data = []
row_count = 0
while row_count < len(df):
    url = df.ix[row_count, 0]
    if url=='na':
	    pass
    else:
    	all_data += [amz_prod_page(url)]
    row_count += 1
    print 'completed', row_count
    with open('amazon_missing_mobiles_reviews.json', 'w') as fw:
        json.dump(all_data, fw, indent=4)
print 'amazon Done'

