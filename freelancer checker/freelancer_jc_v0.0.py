from bs4 import BeautifulSoup
import json
import requests
import time

config_file = open('config.json', 'r') 
config_data = config_file.read()
config = json.loads(config_data)

base_url = config['base_url']
search_query = config['search_query']
interval_page = config['interval_page']
interval = config['interval']

  
def scrape_jobs(page_number):
  
  search_url = f"{base_url}/jobs/{page_number}/?keyword={search_query}"
  response = requests.get(search_url)
  
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    job_listings = soup.find_all('div', class_='JobSearchCard-item')

    if not job_listings:
      print("No job listings found.")
      return None
    else:
      print(f"Found {len(job_listings)} job listings:")
      for job in job_listings:
        title_tag = job.find('a', class_='JobSearchCard-primary-heading-link')
        title = title_tag.get_text(strip=True)
        job_link = "https://www.freelancer.com" + title_tag['href']
        description = job.find('p', class_='JobSearchCard-primary-description').get_text(strip=True)
        budget_tag = job.find('div', class_='JobSearchCard-secondary-price')
        budget = budget_tag.get_text(strip=True) if budget_tag else 'N/A'
        job_id = title_tag['href'].split('/')[-1].split('?')[0] 
                            
        with open('cache.txt' , 'r') as cacheFile :
          projectsIds = cacheFile.read()
          if job_id in projectsIds:
            print("already searched")
            continue
          else:
            projectsIds += (f"{job_id}\n")
            with open('cache.txt', 'w') as cacheFile:
              cacheFile.writelines(projectsIds)
            
            with open('result.txt' , 'r') as infoFile :
              projects_info = infoFile.read()
              projects_info += (f"{title} - {budget} - {job_link}\n")
            with open('result.txt', 'w') as infoFile:
              infoFile.writelines(projects_info)
      return job_listings
  else:
    print(f"Failed to retrieve jobs. Status code: {response.status_code}")
    return None

while True:
  page_number = 1
  job_listing = scrape_jobs(page_number)
  while job_listing:
      page_number += 1
      job_listing = scrape_jobs(page_number)
      time.sleep(interval_page)
  time.sleep(interval)
