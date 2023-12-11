# Selenium-tool-to-web-scrape-job-site
#  This code was used to scrape jobs from a career page of one of a big tech/mobility company.
#    Web driver is first set up to reach the landing page
#    The job postings are identified and the link thereof
#    CSV object is created
#      methods are built to open a new window with each posting
#        Specific desired details are scraped from the current window
#        The window is closed and driver returns to landing page
#        Details are outputed to CSV file using DictWRiter
#      This is repeated for all jobs
# python version: 3.11.5
# selenium version: 4.12.0
#  Installing pip advised
#  OS: windows 10
