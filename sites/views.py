from django.shortcuts import render
from sites.models import Category,CoolSite
from django.core.cache import cache

import requests
import re
import bs4
from bs4 import BeautifulSoup
import json

# Create your views here.

def sites(request):
	categorys = cache.get('sites_categorys')#取缓存
	if not categorys:
		category_list = Category.objects.all()
		categorys=[]
		for category in category_list:
			sites = {
				'category_name':category.name,
				'category_sites':CoolSite.objects.filter(category=category),
			}
			categorys.append(sites)
		cache.set('sites_categorys',categorys,60)
	return render(request,'sites/index.html',{'categorys':categorys})

def hot_topic(request):
	url = 'https://s.weibo.com/top/summary?cate=realtimehot'
	code = 'utf-8'
	topic_list = []
	#code = apparent_encoding
	r = requests.request('GET',url,timeout=5)
	r.raise_for_status()
	r.encoding = code

	html = r.text
	soup = BeautifulSoup(html,'html.parser')
	for tr in soup('tr')[1:11]:
		td_01 = tr('td','td-01')[0]
		td_02 = tr('td','td-02')[0]
		td_03 = tr('td','td-03')[0]
		topic_string = [string for string in td_02.strings if  string!='\n']
		href = 'https://s.weibo.com/' + td_02('a')[0].attrs['href']
		topic_info = {
			'num': td_01.string if td_01.string else '置顶',
			'topic' : topic_string[0],
			'topic_address' : href,
			'topic_hot':topic_string[1] if len(topic_string)>=2 else '',
			}
		topic_list.append(topic_info)
	datas = {
			'topic_list':topic_list,
		}
	return render(request,'sites/hot_topic.html',datas)