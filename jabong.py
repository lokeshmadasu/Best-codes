import urllib2
import ast
import json
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

complete_list=[]

def non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def new_entry_fun(url,price,size,FILE_NAME):
    # print url
    pdpData = {}
    styleImages ={}
    print url
    count=1
    while True:
		try:
		    try:   
		        x = requests.get(url).content
		        soup = BeautifulSoup(x, 'html.parser')
		        body = soup.find('body')
		        script =body.find_all('script')
		        req_script=str(script[0])
		        req_script=req_script.replace('<script type="text/javascript">var globalConfig = ',"")
		        req_script=req_script.replace(';',"")
		        req_script=req_script.replace('</script>',"")
		        req_script=req_script.replace('false',"False")
		        req_script=req_script.replace('true',"True")
		        req_script=req_script.replace('null',"None")
			#print "ok1"
			#print "first try"
		        data=ast.literal_eval(req_script)
		    except urllib2.URLError:
		        #print "io Error"
			print "error while connecting"
		        sleep(10)
		    except AttributeError:
			print "Source not found"
			break
		    
		    div = soup.find('div', {'class': 'content'})
		    try:
			#print "second try"
		        name = div.find("h1")
		    except AttributeError:
		        print "no content found"
		        break
	############################################################ Brand name and product name in Jabong site
		    #print name
		    
		    name_div=name.find_all("span")
		    print "getting"
		    print name_div[0].text
		    pdpData['brandName']= name_div[0].text
		    pdpData['productDisplayName'] = name_div[2].text
		    print pdpData['brandName']
		    print pdpData['productDisplayName']
		    print "Four"
	############################################################### For keys and value pair what given in jabong site
		    sdiv = soup.find("section", {'class': 'prod-info'})
		    ddes =""
		    description = {}
		    descriptio = {}
		    for i in sdiv.find_all("h2"):
		        descri = i.text
		        descri = descri.encode('ascii', 'ignore').encode('utf-8')
		        ddes = str(descri)
		    descriptio['descriptorType'] = "description"
		    s=ddes + name_div[2].text
		    descriptio['value'] = s
		    #print descriptio['value']
		    description['description'] = descriptio
		    pdpData['productDescriptors'] = description
		    desc = sdiv.text

		    try:
		        list = soup.find("ul",{"class":"prod-main-wrapper"}).find_all("span")
		    except AttributeError:
		        #print "Thrid try"
		        break
		    print "five"
		    articleAttributes = {}
		    try:
		        for i in range(0, len(list), 2):
		            key = list[i].text
		            value = list[i + 1].text
		            articleAttributes[key] = value
		            if "Color" in key:
		                pdpData['baseColour'] = value
		                articleAttributes["baseColour"] = value

		            if "Style" in key:
		                articleAttributes["Pattern"] = value

		            if "Sleeves" in key:
		                Sleeve = value
		                articleAttributes["Sleeve"] = Sleeve
		                if "3/4th Sleeves" in Sleeve:
		                    Sleeve = 'Three-Quarter Sleeve'
		                    articleAttributes["Sleeve"] = Sleeve

		            if "Neck" in key:
		                Neck = value
		                if "Mandarin" in Neck:
		                    Neck = "Mandarin / Chinese collar"
		                    articleAttributes["Neck"] = Neck

		            if "Wash Care" in key:
		                articleAttributes["Care"] = value

		            if "Package Contents" in key:
		                articleAttributes["Surface Styling and Features"] = value

		            if "Length" in key:
		                articleAttributes["Dress Length"] = value
		    except IndexError:
		        # print ("Data is Not Proper")
		        break
		    pdpData['articleAttributes'] = articleAttributes


	##################################################################################

		    pdpData['gender'] = "female"
		    pdpData['landingPageUrl'] = url

		    '''size=[]
		    temp_url=url.replace("?utm_source=cps_selekt&utm_medium=dc-clicktracker&utm_campaign=%7Baffiliate_id%7D","")
		    df=pd.read_csv(FILE_NAME)
		    size_row_count=0
		    while size_row_count<len(df):
		        if df.ix[size_row_count,4]=="women_dresses":
		            if temp_url==df.ix[size_row_count, 1]:
		                size=df.ix[size_row_count, 3]
		                break
		        size_row_count+=1'''

		    styleOptions ={}
		    styleOptions["unifiedSize"] = size
		    pdpData['styleOptions'] = styleOptions

		    if len(price)>1:
		        pdpData['discountPercent'] = int(price[2])
		        pdpData['price'] = int(price[0])
		        pdpData['discountedPrice'] =int(price[1])
		    else:
		        pdpData['discountPercent'] = 0
		        pdpData['price'] =int(price[0])
		        pdpData['discountedPrice'] = int(price[0])


		    pdpData['website'] = "jabong"
		    divimg = soup.find_all("div",{"class":"row off-screen"})
		    #print "image processing"
	######################################################################################## Jabong image processing
	###########################################################################HardCode_manula
		    pdpData['fashionType'] = "Fashion"

		    pdpData['ageGroup'] = "Adults-Women"

		    articleType = {'typeName':"Dresses" }
		    pdpData['articleType'] = articleType

		    masterCategory = {"typeName":"Apparel" }
		    pdpData['masterCategory'] = masterCategory

		    subCategory = {"typeName" : "Topwear"}
		    pdpData["subCategory"] = subCategory

		    dict = {}
		    dict['pdpData'] = pdpData

		    file=dict
		    ######################## Product filter begin here  ########################
		    product_filter={}
		    err=[]

		    try:
		        product_filter['dress_shape'] = file['pdpData']['articleAttributes']['Dress Shape'].lower()
		    except KeyError:
		        err+=['dress_shape']
		        product_filter['dress_shape']='na'
		    try:
		        product_filter['pattern_type'] = file['pdpData']['articleAttributes']['Print or Pattern Type'].lower()
		    except KeyError:
		        err+=['pattern_type']
		        product_filter['pattern_type']='na'
		    try:
		        product_filter['body_shape_id'] = file['pdpData']['articleAttributes']['Body Shape ID'].lower()
		    except KeyError:
		        err+=['body_shape_id']
		        product_filter['body_shape_id']='na'
		    try:
		        product_filter['discount_price'] = file['pdpData']['discountedPrice']
		    except KeyError:
		        err+=['discount_price']
		        product_filter['discount_price']=0
		    try:
		        product_filter['knit_or_woven'] = file['pdpData']['articleAttributes']['Knit or Woven'].lower()
		    except KeyError:
		        err+=['knit_or_woven']
		        product_filter['knit_or_woven']='na'
		    try:
		        product_filter['year'] = file['pdpData']['year'].lower()
		    except KeyError:
		        err+=['year']
		        product_filter['year']='na'
		    try:
		        product_filter['age_group'] = file['pdpData']['ageGroup'].lower()
		    except KeyError:
		        err+=['age_group']
		        product_filter['age_group']='na'
		    try:
		        product_filter['broad_category'] = file['pdpData']['subCategory']['typeName'].lower()
		    except KeyError:
		        err+=['broad_category']
		        product_filter['broad_category']='na'
		    try:
		        product_filter['fabric'] = file['pdpData']['articleAttributes']['Fabric'].lower()
		    except KeyError:
		        err+=['fabric']
		        product_filter['fabric']='na'
		    try:
		        product_filter['fit'] = file['pdpData']['articleAttributes']['Fit'].lower()
		    except KeyError:
		        err+=['fit']
		        product_filter['fit']='na'
		    try:
		        product_filter['lining'] = file['pdpData']['articleAttributes']['Lining'].lower()
		    except KeyError:
		        err+=['lining']
		        product_filter['lining']='na'
		    try:
		        product_filter['surface_styling_or_features'] = file['pdpData']['articleAttributes']['Surface Styling'].lower()
		    except KeyError:
		        err+=['surface_styling_or_features']
		        product_filter['surface_styling_or_features']='na'
		    try:
		        product_filter['usage'] = file['pdpData']['usage'].lower()
		    except KeyError:
		        err+=['usage']
		        product_filter['usage']='na'
		    try:
		        product_filter['pattern'] = file['pdpData']['articleAttributes']['Pattern'].lower()
		    except KeyError:
		        err+=['pattern']
		        product_filter['pattern']='na'
		    try:
		        product_filter['sleeves_type'] = file['pdpData']['articleAttributes']['Sleeve Type'].lower()
		    except KeyError:
		        err+=['sleeves_type']
		        product_filter['sleeves_type']='na'
		    try:
		        product_filter['price'] = file['pdpData']['price']
		    except KeyError:
		        err+=['price']
		        product_filter['price']=0

		    product_filter['website'] = "jabong"

		    try:
		        product_filter['season'] = file['pdpData']['season'].lower()
		    except KeyError:
		        err+=['season']
		        product_filter['season']='na'
		    try:
		        product_filter['brand'] = file['pdpData']['brandName'].lower()
		    except KeyError:
		        err+=['brand']
		        product_filter['brand']='na'
		    try:
		        product_filter['fashion_type'] = file['pdpData']['fashionType'].lower()
		    except KeyError:
		        err+=['fashion_type']
		        product_filter['fashion_type']='na'
		    try:
		        product_filter['fabric_2'] = file['pdpData']['articleAttributes']['Fabric 2'].lower()
		    except KeyError:
		        err+=['fabric_2']
		        product_filter['fabric_2']='na'
		    try:
		        product_filter['fabric_3'] = file['pdpData']['articleAttributes']['Fabric 3'].lower()
		    except KeyError:
		        err+=['fabric_3']
		        product_filter['fabric_3']='na'
		    try:
		        product_filter['care'] = file['pdpData']['articleAttributes']['Care'].lower()
		    except KeyError:
		        err+=['care']
		        product_filter['care']='na'
		    try:
		        product_filter['product_line'] = file['pdpData']['articleType']['typeName'].lower()
		    except KeyError:
		        err+=['product_line']
		        product_filter['product_line']='na'
		    try:
		        product_filter['neck'] = file['pdpData']['articleAttributes']['Neck'].lower()
		    except KeyError:
		        err+=['neck']
		        product_filter['neck']='na'
		    try:
		        product_filter['sleeve'] = file['pdpData']['articleAttributes']['Sleeve'].lower()
		    except KeyError:
		        err+=['sleeve']
		        product_filter['sleeve']='na'
		    try:
		        product_filter['gender'] = file['pdpData']['gender'].lower()
		    except KeyError:
		        err+=['gender']
		        product_filter['gender']='na'
		    try:
		        product_filter['colour'] = file['pdpData']['baseColour'].lower()
		    except KeyError:
		        err+=['colour']
		        product_filter['colour']='na'
		    try:
		        product_filter['sub_trend'] = file['pdpData']['articleAttributes']['Sub Trend'].lower()
		    except KeyError:
		        err+=['sub_trend']
		        product_filter['sub_trend']='na'
		    try:
		        product_filter['fashion_category'] = file['pdpData']['masterCategory']['typeName'].lower()
		    except KeyError:
		        err+=['fashion_category']
		        product_filter['fashion_category']='na'
		    try:
		        product_filter['hemline'] = file['pdpData']['articleAttributes']['Hemline'].lower()
		    except KeyError:
		        err+=['hemline']
		        product_filter['hemline']='na'
		    try:
		        product_filter['fabric_type'] = file['pdpData']['articleAttributes']['Fabric Type'].lower()
		    except KeyError:
		        err+=['fabric_type']
		        product_filter['fabric_type']='na'
		    try:
		        product_filter['transparency'] = file['pdpData']['articleAttributes']['Transparency'].lower()
		    except KeyError:
		        err+=['transparency']
		        product_filter['transparency']='na'
		    try:
		        product_filter['discount_percent'] = file['pdpData']['discountPercent']
		    except KeyError:
		        err+=['discount_percent']
		        product_filter['discount_percent']=0
		    try:
		        product_filter['occasion'] = file['pdpData']['articleAttributes']['Occasion'].lower()
		    except KeyError:
		        err+=['occasion']
		        product_filter['occasion']='na'
		    try:
		        product_filter['dress_length'] = file['pdpData']['articleAttributes']['Dress Length'].lower()
		    except KeyError:
		        err+=['dress_length']
		        product_filter['dress_length']='na'

		    try:
		        allsize=[]
		        availability=[]
		        sizedata=size
		        count=0
		        while count<len(sizedata):
		            availability+=[True]
		            count+=1
		        product_filter['all_size']=sizedata
		        #product_filter['size_availability']=availability
		    except KeyError:
		        err+=['all_size']
		        err+['size_availability']
		        product_filter['all_size']=[]
		       # product_filter['size_availability']=[]

		    try:
		        descrip4=file['pdpData']['productDescriptors']['size_fit_desc']['value']
		    except KeyError:
		        descrip4=''

		    try:
		        descrip3=file['pdpData']['productDescriptors']['style_note']['value']
		    except KeyError:
		        descrip3=''
		    try:
		        descrip2=file['pdpData']['productDescriptors']['materials_care_desc']['value']
		    except KeyError:
		        descrip2=''
		    try:
		        descrip1=file['pdpData']['productDescriptors']['description']['value']
		    except KeyError:
		        descrip1=''
		    descrip=descrip1+' '+descrip2+' '+descrip3+' '+descrip4
		    description_soup = BeautifulSoup(descrip, "html.parser")
		    descrip = description_soup.get_text()
		    text2=str(non_ascii(descrip))
		    try:
		        product_filter['product_desription']=text2
		    except (UnicodeDecodeError,UnicodeEncodeError) as e:
		        product_filter['product_desription']=""
		    try:
		        product_filter['display_name']=file['pdpData']['productDisplayName']
		    except KeyError:
		        product_filter['display_name']=""


		    try:
		        file['style_images']=file['pdpData']['styleImages']
		    except KeyError:
		        err+=['styleImages']
		        file['style_images']='na'
		    try:
		        file['pdpData']['landingPageUrl']=url
	
		    except KeyError:
		        file['pdpData']['landingPageUrl']=url
		    try:
		         product_filter['links']=pdpData['landingPageUrl']
	
		    except KeyError:
		         product_filter['links']=pdpData['landingPageUrl']
		    #print file['pdpData']['landingPageUrl']
		    file['product_filter']=product_filter


	############################################  hemline  ############################################################

		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    pro_descp=pro_descp.split()
		    count=0
		    for each in pro_descp:
		        if each=='hem' or each=='hemline':
		            	product_filter['hemline']=pro_descp[count-1]
		        count+=1

	############################################  pattern, pattern type  ############################################################

		    pattern=[
		        "checked",
		        "printed",
		        "self design",
		        "solid",
		        "striped"
		    ]
		    pattern=sorted(pattern,key=len,reverse=True)
		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    pattern_counter=0
		    while pattern_counter<len(pattern):
		        if pattern[pattern_counter] in pro_descp:
		            file['product_filter']['pattern']=pattern[pattern_counter].lower()
		        elif "print" in pro_descp:
		            file['product_filter']['pattern']="printed"

		        pattern_counter+=1
		    pro_descp=pro_descp.split()
		    count=1
		    for each in pro_descp:
		        if each=='print':
		            product_filter['pattern_type']=pro_descp[count-1]
		        count+=1
	############################################  fabric type  ############################################################

		    fabric_type=[
		        "chiffon",
		        "cotton",
		        "crepe",
		        "denim",
		        "georgette",
		        "jacquard",
		        "knitted",
		        "lace or crochet",
		        "crochet",
		        "lace",
		        "linen",
		        "net",
		        "other",
		        "satin finish"
		        "net and georgette"
		        ]
		    fabric_type=sorted(fabric_type,key=len,reverse=True)
		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    fabric_type_counter=0
		    while fabric_type_counter<len(fabric_type):
		        if fabric_type[fabric_type_counter] in pro_descp:
		            file['product_filter']['fabric_type']=fabric_type[fabric_type_counter].lower()
		            break
		        else:
		            file['product_filter']['fabric_type']='na'
		        fabric_type_counter+=1
		    if file['product_filter']['fabric_type']=='na':
		        try:
		            fab_type=file['product_filter']['fabric']
		            for every in fabric_type:
		                if every in fab_type:
		                    file['product_filter']['fabric_type']=every
		                    break
		        except KeyError:
		            file['product_filter']['fabric_type']='na'

	############################################  transperancey  ############################################################

		    transparency=[
		        "opaque",
		        "semi sheer",
		        "sheer"

		        ]
		    transparency=sorted(transparency,key=len,reverse=True)
		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    transparency_counter=0
		    while transparency_counter<len(transparency):
		        if transparency[transparency_counter] in pro_descp:
		            file['product_filter']['transparency']=transparency[transparency_counter].lower()
		            break
		        transparency_counter+=1



	############################################  dress shape  ############################################################

		    dress_shape=[
		        "a-line",
		        "a line",
		        "blouson",
		        "bodycon",
		        "drop-waist",
		        "drop waist",
		        "empire line",
		        "empire-line",
		        "fit and flare",
		        "fit",
			"shift",
			"asymmetric",
			"skater",
		        "flared",
		        "kaftan",
		        "maxi",
		        "peplum",
		        "pinafore or dungaree",
		        "pinafore",
		        "dungaree",
		        "sheath",
			"off shoulder",
		        "shirt",
		        "sweater",
		        "t-shirt",
		        "tshirt",
		        "t shirt",
		        "wrap"
		        ]
		    dress_shape=sorted(dress_shape,key=len,reverse=True)
		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    dress_shape_counter=0
		    while dress_shape_counter<len(dress_shape):
		        if dress_shape[dress_shape_counter] in pro_descp:
		            file['product_filter']['dress_shape']=dress_shape[dress_shape_counter].lower()
		            break
		        dress_shape_counter+=1
	############################################  surface styling  ############################################################

		    surface_styling_or_features=[
		        "applique",
		        "bow",
		        "cut-outs",
		        "cut outs",
		        "embellished",
		        "embroidered",
		        "fringes",
		        "gathered or pleated",
		        "gathered",
		        "pleated",
		        "lace inserts",
		        "lace-up",
		        "lace up",
		        "layered",
		        "leather or faux leather trim",
		        "leather",
		        "faux leather trim",
		        "other",
		        "ruffles",
		        "sheen",
		        "smocked",
		        "tie-ups",
		        "tie ups",
		        ]
		    surface_styling_or_features=sorted(surface_styling_or_features,key=len,reverse=True)
		    pro_descrip=file['product_filter']['product_desription']
		    pro_descrip=u''.join(pro_descrip).encode('utf-8').strip()
		    pro_descp=pro_descrip.lower()
		    surface_styling_or_features_counter=0
		    while surface_styling_or_features_counter<len(surface_styling_or_features):
		        if surface_styling_or_features[surface_styling_or_features_counter] in pro_descp:
		            file['product_filter']['surface_styling_or_features']=surface_styling_or_features[surface_styling_or_features_counter].lower()
		            break
		        surface_styling_or_features_counter+=1
	############################################  sleeve type   ############################################################

		    z =file['product_filter']['sleeves_type']
		    z=z.lower()
		    if z == "cap sleeves":
		        file['product_filter']['sleeves_type']= "cap"

		    elif z == "no sleeves":
		        file['product_filter']['sleeves_type']= "sleeveless"

		    elif z == "roll up sleeves":
		        file['product_filter']['sleeves_type']= "roll up"

		    elif z == "extended or drop shoulder":
		        file['product_filter']['sleeves_type']= "drop shoulder"

	############################################ neck   ############################################################

		    z =file['product_filter']['neck']
		    if z == "keyhole neck":
		        file['product_filter']['neck']= "key hole neckline"

		    elif z == "null":
		        file['product_filter']['neck']=  "na"

		    elif z == "open":
		        file['product_filter']['neck']=  "na"

		    elif z == "other":
		        file['product_filter']['neck']=  "na"

		    elif z == "round":
		        file['product_filter']['neck']= "round neck"

		    elif z == "v neck":
		        file['product_filter']['neck']= "v-neck"

		    elif z == "square":
		        file['product_filter']['neck']= "square neck"

		    if z == "nehru collar":
		        file['product_filter']['neck']= "mandarin / chinese collar"

		    if z == "key hole neckline":
		        file['product_filter']['neck']= "keyhole neck"

		    if z == "polo neck":
		        file['product_filter']['neck']= "turtle neck"

	############################################  common value conversion   ############################################################
		    z =file['product_filter']['dress_length']
		    if z == "mini/short" or z == "short":
		        file['product_filter']['dress_length']= "mini"

		    elif z == "full length" or z == "maxi/long":
		        file['product_filter']['dress_length']=  "maxi"

		    elif z == "knee length":
		        file['product_filter']['dress_length']=  "knee-length"

		    elif z == "calf length" or z == "midi/calf length":
		        file['product_filter']['dress_length']=  "midi"

		    elif z == "3/4th length":
		        file['product_filter']['dress_length']= "cropped length"


	############################################  common value conversion   ############################################################
		    dict=file['product_filter']
		    for key in dict:
		        data= dict[key]
		        try:
		            text=u''.join(data).encode('utf-8').strip()
		            soup = BeautifulSoup(text,"html.parser")
		            data=soup.get_text()
		        except (TypeError,UnicodeDecodeError) as e:
		            pass
		            # print ""
		        try:
		#################################################################################################
		            if data=="solid / plain":
		                dict[key]="solid"
		            elif data=="solid and plian":
		                dict[key]="solid"
		            elif data=="solid":
		                dict[key]="solid"
		            elif data=="embroidered print":
		                dict[key]="embroidered print"
		            elif data=="embroidery print":
		                dict[key]="embroidered print"
		            elif data=="colourblock":
		                dict[key]="colourblocked"
		            elif data=="colourblocked":
		                dict[key]="colourblocked"
		            elif data=="embroidered":
		                dict[key]="embroidered"
		            elif data=="embroidery":
		                dict[key]="embroidered"
		            elif data=="regular wash":
		                dict[key]="regular wash"
		            elif data=="regular wash":
		                dict[key]="regular wash"
		            elif data=="slim fit":
		                dict[key]="slim"
		            elif data=="tapered fit":
		                dict[key]="tapered"
		            elif data=="tapered":
		                dict[key]="tapered"
		            elif data=="comfort fit":
		                dict[key]="comfort"
		            elif data=="comfort":
		                dict[key]="comfort"
		            elif data=="relaxed fit":
		                dict[key]="relaxed"
		            elif data=="relaxed":
		                dict[key]="relaxed"
		            elif data=="loose fit":
		                dict[key]="loose"
		            elif data=="loose":
		                dict[key]="loose"
		            elif data=="classic fit":
		                dict[key]="classic"
		            elif data=="classic":
		                dict[key]="classic"
		            elif data=="skinny fit":
		                dict[key]="skinny"
		            elif data=="skinny":
		                dict[key]="skinny"
		            elif data=="maxi fit":
		                dict[key]="maxi"
		            elif data=="maxi":
		                dict[key]="maxi"
		            elif data=="batgirl":
		                dict[key]="batgirl"
		            elif data=="bat girl":
		                dict[key]="batgirl"
		            elif data=="cult fiction":
		                dict[key]="cult fiction"
		            elif data=="cult fiction":
		                dict[key]="cult fiction"
		            elif data=="cotton spandex(stretchable)":
		                dict[key]="cotton spandex (stretchable)"
		            elif data=="cotton spandex (stretchable)":
		                dict[key]="cotton spandex (stretchable)"
		            elif data=="100%cotton":
		                dict[key]="100% cotton"
		            elif data=="100% cotton":
		                dict[key]="100% cotton"
		            elif data=="100%viscose":
		                dict[key]="100% viscose"
		            elif data=="60%polyester 40%cotton":
		                dict[key]="60% polyester,40% cotton"
		            elif data=="60%cotton 40%polyester":
		                dict[key]="60% cotton,40% polyester"
		            elif data=="70% cotten,30% polester":
		                dict[key]="70% cotton,30% polyester"
		            elif data=="70%cotton 30%polyester":
		                dict[key]="70% cotton,30% polyester"
		            elif data=="95% cotton,5% spandex":
		                dict[key]="95% cotton,5% spandex"
		            elif data=="95% cotton 5% spandex":
		                dict[key]="95% cotton,5% spandex"
		            elif data=="viscose/rayon":
		                dict[key]="viscose/rayon"
		            elif data=="rayon / viscose":
		                dict[key]="viscose/rayon"
		            elif data=="denim spandex(stretchable)":
		                dict[key]="denim spandex (stretchable)"
		            elif data=="denim spandex (stretchable)":
		                dict[key]="denim spandex (stretchable)"
		            elif data=="curved hem":
		                dict[key]="curved"
		            elif data=="high-Low":
		                dict[key]="high low"
		            elif data=="highlighting print":
		                dict[key]="highlight print"
		            elif data=="hip":
		                dict[key]="hip length"
		            elif data=="cropped":
		                dict[key]="cropped length"
		            elif data=="mid-thigh":
		                dict[key]="mid-thigh length"
		            elif data=="v Neck ":
		                dict[key]="v-neck"
		            elif data=="mandarin and chinese collar":
		                dict[key]="mandarin / chinese collar"
		            elif data=="mandarin / chinese collar":
		                dict[key]="mandarin / chinese collar"
		            elif data=="mandarin collar":
		                dict[key]="mandarin / chinese collar"
		            elif data=="turtle or mock neck":
		                dict[key]="turtle neck"
		            elif data=="mock neck":
		                dict[key]="turtle neck"
		            elif data=="5-pockets":
		                dict[key]="5-pocket"
		            elif data=="dot print":
		                dict[key]="doted print"
		            elif data=="a line":
		                dict[key]="a-line"
		            elif data=="short sleeve":
		                dict[key]="short sleeves"
		            elif data=="three quarter sleeves":
		                dict[key]="three quarter sleeves"
		            elif data=="three-quarter sleeves":
		                dict[key]="three quarter sleeves"
		            elif data=="three quarter sleeve":
		                dict[key]="three quarter sleeves"
		            elif data=="three fourth sleeve":
		                dict[key]="three quarter sleeves"
		            elif data=="three fourth sleeves":
		                dict[key]="three quarter sleeves"
		            elif data=="3/4th sleeve":
		                dict[key]="three quarter sleeves"
		            elif data=="3/4th sleeves":
		                dict[key]="three quarter sleeves"
		            elif data=="3/4 sleeve":
		                dict[key]="three quarter sleeves"
		            elif data=="3/4 sleeves":
		                dict[key]="three quarter sleeves"
		            elif data=="3 quaters sleeve":
		                dict[key]="three quarter sleeves"
		            elif data=="no sleeve":
		                dict[key]="sleeveless"
		            elif data=="no sleeves":
		                dict[key]="sleeveless"
		            elif data=="ankle/floor length":
		                dict[key]="ankle length"
		            elif data=="ankle length":
		                dict[key]="ankle length"
		            elif data=="mandarin / chinese collar":
		                 dict[key]="mandarin collar"
		            elif data=="3/4th sleeve":
		                 dict[key]="three quarter sleeve"
		            elif data=="3/4 sleeve":
		                 dict[key]="three quarter sleeve"
		            elif data=="mild distress / ripped":
		                 dict[key]="mild distress"
		            elif data=="high distress / ripped":
		                 dict[key]="high distress"
		            elif data=="block / chunky":
		                 dict[key]="block"
		            elif data=="lace-up / tie-up":
		                 dict[key]="lace-up"
		            elif data=="open/slipper":
		                 dict[key]="slipper"
		            elif data=="ballerina / flat shoes":
		                 dict[key]="ballerina"
		            elif data=="woven design / self prints":
		                 dict[key]="woven design"
		            elif data=="plain/basket weave":
		                 dict[key]="plain"
		            elif data=="zig zag/chevron":
		                 dict[key]="zig zag"
		            elif data=="t-strap / thong sandals":
		                 dict[key]="thong sandals"
		            elif data=="dolman / batwing sleeve":
		                 dict[key]="batwing sleeve"
		            elif data=="waist belt / tie-ups":
		                 dict[key]="waist belt"
		            elif data=="maxi/long":
		                 dict[key]="maxi"
		            elif data=="midi/calf length":
		                 dict[key]="midi"
		            elif data=="boyfriend / boxy":
		                 dict[key]="boyfriend"
		            elif data=="layered/tiered":
		                 dict[key]="layered"
		            elif data=="gathers / pleats":
		                 dict[key]="pleats"
		            elif data=="layered / tiered":
		                 dict[key]="layered"
		            elif data=="sequins / embellishments":
		                 dict[key]="embellishments"
		            elif data=="shimmer / sheen":
		                 dict[key]="shimmer"


		#################################################################################################
		        except AttributeError:
		            pass
		       
		    #dict["links"]=url
		    product_filter=dict
		    return product_filter
		    break
		except (requests.exceptions.ConnectionError, IndexError) as e:
		    print "error while connecting"
		    pass
		    break
	
FILE_NAME="link_jabong_dresses.csv"
#url="http://www.jabong.com/Global_Desi-Black-Coloured-Embroidered-Maxi-Dress-300265627.html"
df=pd.read_csv("link_jabong_dresses.csv")
print len(df)
size=[]
err_urls=[]
row_count=0
count=1
while row_count<len(df):
	size=df.ix[row_count,3]
	s=str(df.ix[row_count,2])
	s=s.replace("[","").replace("]","")
	s=s.split(",")
	price = s
	url=df.ix[row_count,1]
	#print price
	complete_list +=[ new_entry_fun(url,price,size,FILE_NAME)] 
	with open('/home/selekt/Desktop/jabong_dresses.json',"w") as fw:
              json.dump(complete_list,fw,indent=4)
	print "Completed",count
	count+=1
	row_count+=1 
