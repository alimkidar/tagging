from collections import Counter
import pandas as pd
import requests
import json
import re


#------------------ CONFIGURATION -------------------------------
dict_filename = "lib.csv"
input_filename = "convo.csv"


#load convo
convo = pd.read_csv(input_filename)


#nama kolom di "dict_filename"
head_keywords = 'keywords'
head_category1 = 'category1'
head_category2 = 'category2'
head_category3 = 'category3'
head_category_group = 'id_group'

#nama baris di "input_filename"
head_userid = 'userid'
head_username = 'username'
head_caption = 'caption'
head_postid = 'postid'
head_likes_count = 'like_count'
head_comment_count = 'comment_count'
head_brand = 'brand'
head_date_post = 'date_post'



#------------------ OUTPUT FILE -------------------------------
#1. tb_convo_count_percent.csv
#2. tb_pivot_percent.csv
#3. tb_user_statistics.csv
#4. tb_user_keywords.txt


#------------------	FUNCTION DEFINITIONS ------------------------

#Untuk ambil jumlah followers dan following di instagram
def insta(user_name):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	ff = []
	situs = 'https://www.instagram.com/' + user_name + '/'
	try: 
		response = requests.get(url=situs, headers=headers)
	except: 
		print ("Koneksi Internet Error!" + " Username: " + user_name + " Gagal diproses!")
	try:
		json_match = re.search(r'window\._sharedData = (.*);</script>', response.text)
		profile_json = json.loads(json_match.group(1))['entry_data']['ProfilePage'][0]['graphql']['user']


		follower_temp = profile_json['edge_followed_by']['count']
		following_temp = profile_json['edge_follow']['count']
		status_username = True #User ditemukan
	except:
		follower_temp = "-"
		following_temp = "-"
		status_username = False #User tidak ada

	ff.append(follower_temp)
	ff.append(following_temp)
	ff.append(status_username) 
	ff.append(user_name)
	return ff

def hitung_persen(nilai, total):
	try:
		x =  nilai / total
	except:
		x = 0
	return x


#------------------ DATA LOADING --------------------------------

print ("Memulai")

#cek ada data following/followers tidak di convo (headernya kak Fida)
following_exist = False

if 'following' in convo.columns:
	following_exist = True
else:
	print(" ")
	print("[File " + input_filename + " Tidak mempunyai informasi Followers dan Following]")
	print(" ")
loop_ff = True
status_ff = False
while loop_ff == True:
	input_status_ff = input("Perbarui jumlah followers dan following melalui internet? (y/n)")
	if input_status_ff == 'y':
		status_ff = True
		loop_ff = False
	if input_status_ff == 'n':
		status_ff = False
		loop_ff = False
	else:
		print("Masukan salah!")



#load dictionary dari file CSV yang bernama lib2.csv
mydict = {}
dfdict = pd.read_csv(dict_filename)
list_category_group_match =  []
list_category_group = {}
for index, row in dfdict.iterrows():
	keyword = str(row[head_keywords]).replace('"','').replace(",", "").replace("/"," ").replace("("," ").replace(")","").lower()
	category1 = str(row[head_category1]).lower()
	category2 = str(row[head_category2]).lower()
	category3 = str(row[head_category3]).lower()
	
	if len(category1) == 0:
		category1 = 'not-available'	
	if len(category2) == 0:
		category2 = 'not-available'
	if len(category3) == 0:
		category3 = 'not-available'

	category_group = str(row[head_category_group])
	if category_group not in list_category_group:
		list_category_group[category_group] = []

		list_category_group[category_group].append(category1)
		list_category_group[category_group].append(category2)
		list_category_group[category_group].append(category3)
	mydict[keyword] = category_group
	list_category_group_match.append(category_group)
list_category_group_match = list(set(list_category_group_match))
str_category_group = ""
str_sumof_interest = ""

#List jumlah category (dapat menyesuaikan, sesuai lib2.csv)
for i in list_category_group_match:
	str_category_group = str_category_group + "," + i
	str_sumof_interest = str_sumof_interest + ",sum_of_" + i 



#Seting Output1
output_name = "tb_convo_count_percent.csv"
f = open(output_name, "w", encoding="utf-8")
label = "Username,PostID,Date,Convo" + str_category_group + "\n"
f.write(label)

#Seting Output2
output_name2 = "tb_pivot_percent.csv"
g = open(output_name2, "w", encoding="utf-8")
label2 = "Username" + str_sumof_interest + "\n"
g.write(label2)

#Seting Output3
output_name3 = "tb_statistic_user.csv"
h = open(output_name3, "w", encoding="utf-8")
label3 = "Username,Total Post,Total Likes,Average Like,Total Comment,Average Comment,Engagement,Followers,Following,Reach\n"
h.write(label3)

#Seting Output4
output_name4 = "tb_user_keywords.txt"
z = open(output_name4, "w", encoding="utf-8")
label4 = "Username,PostID,Caption,Keyword,IDGroup\n"
z.write(label4)

#Seting Output5
output_name5 = "tb_statistic_convo.csv"
f5 = open(output_name5, "w", encoding="utf-8")
labelf5 = "Brand,Username,PostID,Conversation,Time Stamp,Likes,Comments,Engagement\n"
f5.write(labelf5)

#Seting Output6
output_name6 = "tb_statistic_convo_group.csv"
f6 = open(output_name6, "w", encoding="utf-8")
labelf6 = "Username,PostID,Conversation,Time Stamp,Likes,Comments,Engagement,ID_Group,Category1,Category2,Category3\n"
f6.write(labelf6)

#Seting Output7
output_name7 = "tb_statistic_group.csv"
f7 = open(output_name7, "w")
labelf7 = "ID_Group,Category1,Category2,Category3,Count,Engagement\n"
f7.write(labelf7)

#Seting Output8
output_name8 = "tb_statistic_attribute.csv"
f8 = open(output_name8, "w")
labelf8 = "Category,Attribute,Count\n"
f8.write(labelf8)


hit = 1
hit_user = 1

#Data merupakan sebuah kumpulan kata secara temporary pada setiap caption (BERSIFAT TEMPORARY)
data = []

#perhitungan tiap post
post = []

#mencatat ID Group di setiap convo
post_id_group = {}
all_post_id_group = []

#perhitungan untuk semua post
user_post = {}

#data user list
user_list = []

#Pencatatan. Hasilnya nantinya akan | count_user_posts['username'] = jumlah post |
count_user_posts = {}
count_user_likes = {}
count_user_comments = {}
count_user_followers = {}
count_user_following = {}

#Hitung engagement per post
post_engagement = {}
# Mengolah Convo
df1 = pd.DataFrame()
for index, row in convo.iterrows():
	user_id = row[head_userid].replace('"', '')
	username = row[head_username].replace('"',"").replace(",","|")
	caption = str(row[head_caption]).replace(",","").replace(r"\u","|").replace("\r","").replace("\n","").lower().strip()
	post_id = row[head_postid].replace('"','')
	post_id_group[post_id] = []
	brand = row[head_brand]
	date_post = str(row[head_date_post])
	count_likes = str(row[head_likes_count])
	count_comments = str(row[head_comment_count])
	engagement_value = str(row[head_likes_count] + row[head_comment_count])

	post_engagement[post_id] = engagement_value

	#labelf5 = "Brand,Username,Conversation,Time Stamp,Likes,Comments,Engagement\n"
	linef5 = brand + "," + username + ",'" + str(post_id) + "," + caption + "," + date_post + "," + count_likes + "," + count_comments + "," + engagement_value + "\n"
	f5.write(linef5)

	if following_exist == True:
		if username not in count_user_followers:
			count_user_followers[username] = row['followers']
			count_user_following[username] = row['following'] 

	hit += 1
	if username not in user_list:
		user_list.append(username)


	#Mengecek apakah username sudah masuk di dalam count_user_post
	if username not in count_user_posts:
		count_user_posts[username] = 1
	else: 
		count_user_posts[username] += 1

	if username not in count_user_likes:
		count_user_likes[username] = row[head_likes_count]
	else:
		count_user_likes[username] += row[head_likes_count]

	if username not in count_user_comments:
		count_user_comments[username] = row[head_comment_count]
	else:
		count_user_comments[username] += row[head_comment_count]

	#Untuk mencocokan keyword dalam caption
	for i in mydict:
		if i in caption:
			post.append(mydict[i])
			post_id_group[post_id].append(mydict[i]) #mydict[i] isinya IDGroup
			all_post_id_group.append(mydict[i])
			x_id_grup = mydict[i]

			cat1_ = list_category_group[x_id_grup][0]
			cat2_ = list_category_group[x_id_grup][1]
			cat3_ = list_category_group[x_id_grup][2]

			#menulis CSV tentang keyword yang cocok dengan convo/caption yang kena
			isi = (str(username) + ',"' + str(post_id) + '",' + str(caption) + "," + str(i) + "," + str(mydict[i]) + "\n")
			
			if type(isi) != bytes:
				isi = isi.encode('utf-8')
			#labelf6 = "Username,PostID,Conversation,Time Stamp,Likes,Comments,Engagement,ID_Group,Category1,Category2,Category3\n"
			id_group = str(x_id_grup)
			linef6 = (username + ",'" + post_id + "," + caption + "," + 
				date_post + "," + count_likes + "," + count_comments + "," + engagement_value + "," + id_group + "," +  
				cat1_ + "," + cat2_ + "," + cat3_ + "\n")

			df1 = df1.append(pd.DataFrame([[id_group,int(engagement_value)]],columns=['id_group','value']))

			isi = str(isi)
			f6.write(linef6)
			z.write(isi)

	
	#Sebagai counter. atau perhitungan jumlah berapa interest nya (travel, berapa culinary, berapa musik, dll)
	counter = Counter(post)
	post = []
	total_keyword = sum(counter.values())
	

	#Mengambil nilai dari setiap interestnya, dan menyimpannya dalam satu data list
	nilai_interets = {}
	str_nilai_interest = ""

	#####NILAI Interestharus dikode
	for i in list_category_group_match:
		nilai_interets[i] = hitung_persen(counter[i], total_keyword)
		str_nilai_interest = str_nilai_interest + "," + str(nilai_interets[i])

		#label = "Username,PostID,Date,Convo" + str_category_group + "\n"
	line = username + ",'" + str(post_id) + "," + date_post + "," + caption + str_nilai_interest + "\n"
	f.write(line)

	if username not in user_post:
		user_post[username] = {}

	#menghitung jumlah interest dari masing2 user (semua post)
	for i in list_category_group_match:
		if str(i) not in user_post[username]:
			user_post[username][i] = 0
		user_post[username][i] += nilai_interets[i]


counter_all_id_group = Counter(all_post_id_group)

#harus per id group
#labelf7 = "ID_Group,Category1,Category2,Category3,Count,Engagement\n"
#SUMIF
df2 = df1.groupby("id_group")["value"].sum()

for i in list_category_group:
	#id_group_sum_if = df1.query("id_group" == i)["value"].sum()
	#id_group_sum_if = df1.loc[df1.id_group == i, "value"].sum()
	if i not in df2:
		id_group_sum_if = 0
	else:
		id_group_sum_if = df2[i]
	count_key_per_category = counter_all_id_group[i]
	#y_id_grup = [mydict][i]
	linef7 = (str(i) + "," + list_category_group[i][0] + "," + list_category_group[i][1] + 
		"," + list_category_group[i][2] + "," + str(count_key_per_category) + "," 
		+ str(id_group_sum_if) + "\n")
	f7.write(linef7)
f7.close()
f6.close()
f5.close()
df_f6 = pd.read_csv(output_name6)
df3 = pd.DataFrame()

all_category = {}
#labelf8 = "Category,Attribute,Count\n"
for index, row in df_f6.iterrows():
	cat1__ = row['Category1'].lower()
	cat2__ = row['Category2'].lower()
	cat3__ = row['Category3'].lower()

	if cat1__ not in all_category:
		all_category[cat1__] = 'Category1'
	if cat2__ not in all_category:
		all_category[cat2__] = 'Category2'
	if cat3__ not in all_category:
		all_category[cat3__] = 'Category3'

	df3  = df3.append(pd.DataFrame([['Category1',cat1__],['Category2',cat2__],['Category3',cat3__]],columns=["Category","Attribute"]))
df3_counter = df3.groupby('Attribute').size()
for i in all_category:

	linef8 = all_category[i] + "," + i + "," + str(df3_counter[i]) + "\n"
	f8.write(linef8)

f8.close()
#df3_counter = df3_counter.set_index([0,1])

print (" ")
print ("Profiling...")
print (" ")

for i in user_list:

	#i = username

	str_nilai_interest_user = ""
	for j in user_post[i]:
		 str_nilai_interest_user = str_nilai_interest_user + "," + str(user_post[i][j])


	#total_percent = user_post[i]['traveling'] + user_post[i]['fashion'] + user_post[i]['culinary'] + user_post[i]['music']
	total_percent = sum(user_post[i].values())
	str_percent_total = ""
	percent_total = {}
	for j in list_category_group_match:
		percent_total[j] = hitung_persen(user_post[i][j], total_percent)
		str_percent_total = str_percent_total + "," + str(percent_total[j])

	#Header = "Username,Sum of interest"
	g.write(str(i) + str_percent_total + "\n")

	average_likes = count_user_likes[i] / count_user_posts[i]
	average_comments = count_user_comments[i] / count_user_posts[i]

	engagement = average_likes + average_comments

	###Scrape
	if status_ff == True:
		if i not in count_user_followers:
			count_user_followers[i] = insta(i)[0]
		if i not in count_user_following:
			count_user_following[i] = insta(i)[1]
		#user_reach = count_user_posts[i] * (0.3 * count_user_followers[i])
	else:
		if following_exist == False:
			print("Following Eksis False")
			if i not in count_user_followers:
				count_user_followers[i] = 'nan.'
			if i not in count_user_following:
				count_user_following[i] = 'nan.'
	if count_user_followers[i] != 'nan.':
		user_reach = count_user_posts[i] * (0.3 * count_user_followers[i])


	#Header = "Username,Total Post,Total Likes,Average Like,Total Comment,Average Comment,Engagement,Followers,Following,Reach\n"
	h.write(str(i) + "," + str(count_user_posts[i]).replace(",","|") + "," + str(count_user_likes[i]).replace(",","|") + "," + str(average_likes).replace(",","|") + "," + str(count_user_comments[i]).replace(",","|") + "," + str(average_comments).replace(",","|") + "," + str(engagement) + "," + str(count_user_followers[i]).replace(",","|") + "," + str(count_user_following[i]).replace(",","|") + "," + str(user_reach) + "\n")
	print (str(hit_user) + ". Username: " + i  + " Followers: " + str(count_user_followers[i]) + ". Following: " + str(count_user_following[i]) + ".")
	hit_user += 1

f.close()
g.close()
h.close()
z.close()
print("Data Tersimpan")
print("Proses Selesai")