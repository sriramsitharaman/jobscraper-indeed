from urllib.request import urlopen
#import urllib2
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime as d

role = input("Enter role - ")
city = input("Enter city - ")
state =input("Enter two-letter state - ")
df = pd.DataFrame()

final_role = role.split()
final_role = '+'.join(word for word in final_role)

final_city = city.split()
final_city = '+'.join(word for word in final_city)

url = "https://www.indeed.com/jobs?as_and=" + final_role + "&radius=5" + "&l=" + final_city + "%2C" + state + "&jt=fulltime&fromage=1&limit=10&sort=date"
page = urlopen(url)
target = BeautifulSoup(page,'html.parser')

#jobCount = re.findall('\d+', target.find(id = 'searchCount').string.encode('utf-8'))

jobCount=int(target.find(id = 'searchCount').text.split()[-1].replace(",",""))
print ("Total Jobs :",jobCount)
#if len(jobCount) > 3:
#	total_num_jobs = (int(jobCount[2])*1000) + int(jobCount[3])
#else:
#	total_num_jobs = int(jobCount[2])

#print ('%d new jobs found' % jobCount)  
num_pages = int(jobCount/10)

roleList=role.split(" ")
print (roleList)
finalJobCount=0
for page in range(1,num_pages+1):
	
	start_from = (page-1)*10
	
	final_url = url + "&start=" + str(start_from)
	page = urlopen(final_url).read()
	target = BeautifulSoup(page, "lxml")
	targetElements = target.find_all('div', attrs={'data-tn-component': 'organicJob'})

	# trying to get each specific job information (such as company name, job title, urls, ...)
	for elem in targetElements: 
		comp_name = elem.find('span', attrs={'itemprop':'name'}).getText().strip()
		job_title = elem.find('a', attrs={'class':'turnstileLink'}).attrs['title']
		home_url = "https://www.indeed.com"
		job_link = "%s%s" % (home_url,elem.find('a').get('href'))
		job_addr = elem.find('span', attrs={'itemprop':'addressLocality'}).getText()
		job_posted = elem.find('span', attrs={'class': 'date'}).getText()
		try:
			flag=0
			if len(roleList)>1:
				for i in roleList:
					#print (i,job_title.lower())
					if i.lower() in job_title.lower():
						flag+=1
		except:
			flag=0
		
		# add a job info to our data frame if it contains the ob title
		if flag==len(roleList):
			df = df.append({'comp_name': comp_name, 'job_title': job_title, 
						'job_link': job_link, 'job_posted': job_posted,
						'job_location': job_addr
					   }, ignore_index=True)
			finalJobCount+=1

print ('Jobs Added now - ', finalJobCount, 'new jobs found')
df = df[['job_title','comp_name','job_location','job_posted','job_link']]
df.to_csv('./jobs_' + str(d.datetime.now().strftime("%Y%m%d-%H%M%S")) + '.csv', encoding = 'utf-8', index=False)