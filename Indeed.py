import urllib2
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime as d

role = raw_input("Enter role - ")
city = raw_input("Enter city - ")
state = raw_input("Enter two-letter state - ")
df = pd.DataFrame()

final_role = role.split()
final_role = '+'.join(word for word in final_role)

final_city = city.split()
final_city = '+'.join(word for word in final_city)

url = "https://www.indeed.com/jobs?as_and=" + final_role + "&radius=5" + "&l=" + final_city + "%2C" + state + "&jt=fulltime&fromage=1&limit=10&sort=date"
page = urllib2.urlopen(url)
target = BeautifulSoup(page,'html.parser')

jobCount = re.findall('\d+', target.find(id = 'searchCount').string.encode('utf-8'))

if len(jobCount) > 3:
	total_num_jobs = (int(jobCount[2])*1000) + int(jobCount[3])
else:
	total_num_jobs = int(jobCount[2])

print '%d new jobs found' % total_num_jobs  
num_pages = total_num_jobs/10

for page in range(1,num_pages+1):
	
	start_from = (page-1)*10
	
	final_url = url + "&start=" + str(start_from)
	page = urllib2.urlopen(final_url).read()
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

		# add a job info to our data frame
		df = df.append({'comp_name': comp_name, 'job_title': job_title, 
						'job_link': job_link, 'job_posted': job_posted,
						'job_location': job_addr
					   }, ignore_index=True)

print 'Done with collecting the job postings - ', total_num_jobs, 'new jobs found'
df = df[['job_title','comp_name','job_location','job_posted','job_link']]
df.to_csv('./jobs_' + str(d.datetime.now().strftime("%Y%m%d-%H%M%S")) + '.csv', encoding = 'utf-8', index=False)