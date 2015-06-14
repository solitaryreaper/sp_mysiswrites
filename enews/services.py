from bs4 import BeautifulSoup
import urllib2, json
from enews.models import Article
from dateutil import parser
import string
import time
from django.utils.encoding import iri_to_uri

GOOGLE_CS_BASE_URL = "https://www.googleapis.com/customsearch/v1?q=barkha+kumari&cx=006143742932700250436%3Ajgjtarwwroa&key=AIzaSyAOIBrG7N9F8UF8GBci-XWMdOYqnhdiGNg"

# Parses the json data returned by google custom search api and returns a set of URLs
def parse_google_cs_api_json_results(url):
    article_url_links = None
    try:
        json_data = urllib2.urlopen(url)
        json_obj = json.load(json_data)
        article_url_links = []
        for url in json_obj['items']:
            article_url_links.append(url['link'])
        print str(article_url_links)
    except Exception, err:
        print "Failed to get results using google custom search for " + url
        print err
    
    return article_url_links

# Parses the news article page and extracts relevant content
def parse_dc_article_page(url):
    url = iri_to_uri(url)
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)

    print "URL : " + url
        
    article = None
    try:
        title = soup.find(id="page-title").text.strip()
        title = str(filter(lambda x: x in string.printable, title))
        print "Title : " + title
        
        publish_date_string = soup.find('footer', {'class' : 'submitted'}).findChild('span').text.strip()
        publish_date = parser.parse(publish_date_string)
        
        categories = ""
        categories_tag = soup.find('div', {'class' : 'breadcrumb'}).findChildren('a')
        for category in categories_tag:
            if category is not None:
                if categories == "":
                    categories = categories + " " + str(category.text.strip())
                else:
                    categories = categories + ", " + str(category.text.strip())
    
        # remove the home category as it is too generic
        categories = categories.replace("Home,", "")
        categories = categories.strip()
        print "Categories : " + str(categories)
        
        snippet = soup.find('div', {'class' : 'field-item even', 'property' : 'content:encoded'})
        snippet_text = snippet.text[0:140] + " ... "
        print "Snippet : " + str(filter(lambda x: x in string.printable, snippet_text))
        
        article = Article(title=title, url=url, snippet=snippet_text, publish_date=publish_date, categories=categories)
    except Exception, err:
        print "Failed to parse URL : " + url + " : " + str(err)
    
    return article
        
# Daily job that checks for any recent article based on the filters
def run_daily_update_job():
    print "Inside the daily update job .."
    top_article_links = parse_google_cs_api_json_results(GOOGLE_CS_BASE_URL + "&sort=date")
    result = ingest_article_links(top_article_links)
    return result

"""
    A bootstrap job that fetches all the relevant articles and populates the database
    1) Call google custom search API and get JSON results.
    2) Parse JSON data to get article URLs.
    3) Parse each URL to get article info.
    4) Persist information in database.
"""
def run_bootstrap_job():
    print "Inside the bootstrap update job .."
    article_start_index = 1
    are_results_over = False
    total_articles_ingested = 0
    while not are_results_over:
        url = GOOGLE_CS_BASE_URL + "&start=" + str(article_start_index)
        print "Parsing for URL : " + url
        article_start_index = article_start_index + 10
        time.sleep(2)
        links = parse_google_cs_api_json_results(url)
        if not links:
            print "All articles ingested .."
            are_results_over = True
        else:
            output = ingest_article_links(links)
            total_articles_ingested += output

    return "Total articles ingested : " + str(total_articles_ingested)

"""
    Ingest the articles and useful content into the database
"""
def ingest_article_links(links):
    num_new_articles_ingested = 0 
    for link in links:
        if not Article.objects.filter(url=link).exists():
            article = parse_dc_article_page(link)
            if article is not None:
                article.save()
                print "Successfully saved article for url : " + link
                num_new_articles_ingested = num_new_articles_ingested + 1
            else:
                print "Failed to parse URL " + link
        else:
            print "Article for URL " + link + " already exists .."
            
    return num_new_articles_ingested
        
        
if __name__ == '__main__':
    #parse_dc_article_page('http://www.deccanchronicle.com/131209/lifestyle-offbeat/article/mud-so-what')
    pass
    
