import requests
import json
import time

config_file = open('config.json', 'r') 
config_data = config_file.read()
config = json.loads(config_data)

base_url = config['base_url']
search_query = config['search_query']
interval = config['interval']
interval_page = config['interval_page']
min_budget = config['min_budget'] 
max_budget = config['max_budget'] 

def scrape_jobs(code):
    global done
    global page_check
    
    search_url = f"{base_url}/ajax/table/project_contest_datatable.php?tag={search_query}&type=false&budget_min={min_budget}&budget_max={max_budget}&contest_budget_min=false&contest_budget_max=false&hourlyrate_min=false&hourlyrate_max=false&hourlyProjectDuration=false&skills_chosen=false&languages=false&status=open&vicinity=false&countries=false&lat=false&lon=false&iDisplayStart={code}&iDisplayLength=50&iSortingCols=1&iSortCol_0=6&sSortDir_0=desc&format_version=3&"

    response = requests.get(search_url)

    if response.status_code == 200:
        data = json.loads(response.text)
        page_check =  False
        
        if (data and 'aaData' in data) and (data['aaData'] != []):
            job_listings = data['aaData']
            for job in job_listings:
                job_id = job['project_id']
                title = job['project_name']
                description = job['project_desc'] 
                budget = job['budget_range'] if 'budget_range' in job else 'N/A'
                link = job['seo_url'] if 'seo_url' in job else "N/A"
                job_link=  f"{base_url}{link}"
                
                try:
                    with open('cache.txt' , 'r') as cacheFile :
                        projectsIds = cacheFile.read()
                        if str(job_id) in projectsIds:
                            page_check = True
                        else:
                            print(f"Title: {title}")
                            print(f"Description: {description}")
                            print(f"Budget: {budget}")
                            print('-' * 80)
                            projectsIds += (f"{job_id}\n")
                            with open('cache.txt', 'w') as cacheFile:
                                cacheFile.writelines(projectsIds)
                            
                            with open('result.txt' , 'r') as infoFile :
                                projects_info = infoFile.read()
                                projects_info += (f"{title} == {budget} == {job_link}\n")
                            with open('result.txt', 'w') as infoFile:
                                infoFile.writelines(projects_info)
                except Exception as e:
                    print(e)
        else:
            done = True
            print("No more job listings found or failed to retrieve job listings.")
            return None
    else:
        print(f"Failed to retrieve job listings. Status code: {response.status_code}")
        return None
    
def get_jobs():
    while True:
        page_number = 0
        done = False
        while not done:
            scrape_jobs(page_number)
            
            if page_check == True:
                print("cycle done, no other new jobs")
                break
            
            page_number += 50
            time.sleep(interval_page)
        time.sleep(interval)
        
def get_first_page_salary_job_analytics():
    search_url = f"{base_url}/ajax/table/project_contest_datatable.php?tag={search_query}&type=false&budget_min=false&budget_max=false&contest_budget_min=false&contest_budget_max=false&hourlyrate_min=false&hourlyrate_max=false&hourlyProjectDuration=false&skills_chosen=false&languages=false&status=open&vicinity=false&countries=false&lat=false&lon=false&iDisplayStart=0&iDisplayLength=50&iSortingCols=1&iSortCol_0=6&sSortDir_0=desc&format_version=3&"

    response = requests.get(search_url)

    if response.status_code == 200:
        data = json.loads(response.text)
        joblist = data["aaData"]

        highest = 0
        sum = 0
        for job in joblist:
            budget_max = job['maxbudget'] if 'maxbudget' in job else 0
            budget_min = job['minbudget'] if 'minbudget' in job else 0
            
            if budget_max != 0:
                budget_min = int(budget_min.replace('$', ''))
                budget_max = int(budget_max.replace('$', ''))
                sum += budget_max - budget_min
            if budget_max > highest:
                highest = budget_max
                
        for x in joblist:
            if x['maxbudget'] == f'${highest}':
                title = x['project_name']
                link = x['seo_url'] if 'seo_url' in x else "N/A"
                job_link=  f"{base_url}{link}"
        avg = sum / len(joblist)
        print(f'highest job salary ==> {title} == {highest} == {job_link}, total average salary ==> {avg}')
    else:
        print("Failed")
        return None
    
get_first_page_salary_job_analytics()
get_jobs()