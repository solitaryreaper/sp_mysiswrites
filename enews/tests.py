from bs4 import BeautifulSoup
import urllib2, string
from dateutil import parser

# Parses the news article page and extracts relevant content
def parse_dc_article_page(url):
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)

    print "URL : " + url
    
    article = None
    try:
        title, publish_date, categories, snippet_text = "NA", "NA", "NA", "NA"
        
        try:
            title = soup.find(id="page-title").text
            title = str(filter(lambda x: x in string.printable, title))
            print "Title : " + title
        except:
            print "Failed to extract title for URL : " + url
        
        try:
            publish_date_string = soup.find('footer', {'class' : 'submitted'}).findChild('span').text
            print "Publish Date : " + publish_date_string
            publish_date = parser.parse(publish_date_string)
        except:
            print "Failed to extract publication date for URL : " + url
        
        try:
            categories = ""
            categories_tag = soup.find('div', {'class' : 'breadcrumb'}).findChildren('a')
            for category in categories_tag:
                if category is not None:
                    if categories == "":
                        categories = categories + " " + str(category.text)
                    else:
                        categories = categories + ", " + str(category.text)
                        
            # remove the home category as it is too generic
            categories = categories.replace("Home,", "")
            categories = categories.strip()
            print "Categories : " + str(categories)                        
        except:
            print "Failed to extract categories for URL : " + url
    
        try:        
            snippet = soup.find('div', {'class' : 'field-item even', 'property' : 'content:encoded'})
            print str(snippet)
            snippet_text = snippet.text[0:140] + " ... "
            print "Snippet : " + str(filter(lambda x: x in string.printable, snippet_text))
        except :
            print "Failed to extract snippet for URL : " + url
        
    except Exception, err:
        print "Failed to parse URL : " + url + " : " + str(err)
    
    return article

def get_all_sorted_time_keys(min_year, max_year, min_key, max_key):
    sorted_keys = []
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    for year in range(min_year, max_year + 1):
        for month in months:
            key = str(year) + str(month)
            if key < min_key or key > max_key:
                continue

            sorted_keys.append(key)

    print "Keys : " + str(sorted_keys)
    return sorted_keys

if __name__ == '__main__':
    get_all_sorted_time_keys(2012, 2015, "201210", "201506")
    #parse_dc_article_page('http://archives.deccanchronicle.com/130319/lifestyle-booksart/article/symbol-womb')
    #parse_dc_article_page('http://archives.deccanchronicle.com/130521/lifestyle-offbeat/article/%E2%80%98indians-are-not-copycats%E2%80%99-dr-krishna-m-ella')    
    #parse_dc_article_page('http://www.deccanchronicle.com/140106/news-current-affairs/article/horror-atm-0')
    #parse_dc_article_page('http://archives.deccanchronicle.com/130317/lifestyle-booksart/article/wood-you-it')
    #parse_dc_article_page('http://www.deccanchronicle.com/131226/lifestyle-health-and-well-being/article/%E2%80%98my-waistline-20-inches-slimmer%E2%80%99')
    
