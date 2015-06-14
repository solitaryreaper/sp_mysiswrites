from django.db import models

# Models a single news article

class Article(models.Model):
    title = models.CharField(max_length=200) # title of news article
    url = models.CharField(max_length=500)  #url for news article
    snippet = models.CharField(max_length=1000) # snippet for news article
    publish_date = models.DateField()   # publication date of news article
    categories = models.CharField(max_length=100) # category of news article

    def __eq__(self, other):
        return self.url == other.url

    def __str__(self):
        return self.title    
   
   
    
    