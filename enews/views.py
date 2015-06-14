from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.encoding import iri_to_uri
import json
from django.contrib.syndication.views import Feed

from enews.models import Article

from enews.services import run_daily_update_job, run_bootstrap_job, parse_dc_article_page

# Retrieves all the news articles on the home page dashboard
def index(request):
    articles = set(Article.objects.all())
    context = RequestContext(request, {'articles': articles})
    return render(request, 'enews/index.html', context)    

def trends(request):
    return render(request, 'enews/trends.html') 

def get_category_stats(request):
    """
        Gets the count of all news articles by categories
    """
    category_stats = {}
    for article in set(Article.objects.all()):
        categories = article.categories.split(",")
        for category in categories:
            category = category.strip()
            if category in category_stats.keys():
                category_stats[category] = category_stats[category] + 1
            else:
                category_stats[category] = 1
                
    categories, num_articles = [], []
    for category,count in category_stats.items():
        categories.append(category)
        num_articles.append(count)
        
    data = {'categories': categories, 'num_articles': num_articles}                       
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_timeline_stats(request):
    """
        Returns the number of articles per month
    """
    timeline_stats = {}
    for article in set(Article.objects.all()):
        publish_date = article.publish_date
        year_month_str = str(publish_date.year)
        month = publish_date.month
        year_month_str = year_month_str + (str(month) if (len(str(month)) == 2) else ("0" + str(month)))
        
        if year_month_str in timeline_stats.keys():
            timeline_stats[year_month_str] = timeline_stats[year_month_str] + 1
        else:
            timeline_stats[year_month_str] = 1
    
    num_articles = []

    sorted_keys = sorted(timeline_stats.keys())
    min_key = sorted_keys[0]
    max_key = sorted_keys[-1]
    min_year = int(min_key[:4])
    max_year = int(max_key[:4])

    all_sorted_keys = get_all_sorted_time_keys(min_year, max_year, min_key, max_key)
    for key in all_sorted_keys:

        if key in timeline_stats:
            num_articles.append(timeline_stats[key])
        else:
            num_articles.append(0)

    print "Articles : " + str(num_articles)
    data = {'num_articles': num_articles}
    return HttpResponse(json.dumps(data), content_type='application/json')    

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

def dailyjob(request):
    result = run_daily_update_job()
    return HttpResponse("Ran the daily update job. Results : " + result)

def bootstrapjob(request):
    result = run_bootstrap_job()
    return HttpResponse("Ran the bootstrap job .." + result)

def ingest(request, url):
    """
        Ingests a single URL into the database
    """
    url = iri_to_uri(url)
    print "Ingesting URL : " + url
    article = parse_dc_article_page(url)
    is_success = False
    does_article_exist = False
    reason = ""
    if article is not None:
        try:
            if not Article.objects.filter(url=url).exists():            
                article.save()
                is_success = True
            else:
                print "Article for URL " + url + " already exists !! "
                does_article_exist = True
        except Exception, err:
            print "Error while saving article for url " + url
            reason = str(err)
    else:
        reason = "Article is NULL"

    response = ""
    if does_article_exist:
        response = "Article for URL : " + url + " already exists !!"
    elif is_success:
        response = "Successfully ingested article : " + url
    else:
        response = "Failed to ingest article : " + url + ", Reason = " + reason
        
    return HttpResponse(response)

class ArticlesFeed(Feed):
    """
        Returns the feed containing latest articles for this site ..
    """
    title = "Barkha's articles in Deccan Chronicle .."
    link = "/enews/"
    description = "Latest articles by Barkha in Deccan Chronicle .."
    
    def items(self):
        return Article.objects.order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.snippet

    def item_link(self, item):
        return item.url    
