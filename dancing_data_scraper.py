import bs4
import requests
import re
from event import Event
import datetime
from dateutil.parser import parse

URL_SP = 'http://www.swingplanit.com'
URL_DC = 'http://dancecal.com/?sMon=9&sYear=2016&num=12&hidetype=&list=1&theme=&hidedanceIcon='
splitters = ['?', ':']
event_list =[]
event_name_list = []
dates = []
dates_formatted = []
def get_soup(url):
    """Download and convert to BeautifulSoup."""
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return soup

def scrape_swing_planit():
	soup = get_soup(URL_SP)
	for event_list_item in soup.findAll('li', {'class' : 'color-shape'})[0:8]:
		for a_tag in event_list_item.findAll('a', href=True):
			event_soup = get_soup(a_tag['href'])
			event = Event()
			event.name = event_soup.title.text
			event_name_list.append(event.name)
			event.details = event_soup.findAll('p')[0].text
			event.teachers = event_soup.findAll('p')[2].text.split(', ')
			li_tags = event_soup.findAll('li')
			for li in li_tags:
				li_text = (li.get_text())
				for splitter in splitters:
					if splitter in li_text:
						print(event.name + li_text.split(splitter,1)[0] + ': ' + 
							  li_text.split(splitter,1)[1])
						try:
							if li_text.split(splitter,1)[0].lower() == 'when':
								date_range = li_text.split(splitter,1)[1].strip()
								date_range = date_range.split(' - ')
								event.start_date = parse(date_range[0])
								event.end_date = parse(date_range[1])
						except:
							import pdb; pdb.set_trace()
						if li_text.split(splitter,1)[0].lower() == 'country':
							event.country = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'town':
							event.city = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'website':
							event.url = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'styles':
							event.dance_styles = li_text.split(splitter,1)[1].lower().strip().split(',')
			event_list.append(event)
	return event_list

def scrape_dance_cal():
	soup = get_soup(URL_DC)
	for event_div in soup.findAll('div', {'class' : 'DCListEvent'})[0:20]:
		event = Event()
		for span in event_div.findAll('span'):
			if 'DCEventInfoDate' in span['class']:
				event.start_date = parse(span.text)
			if 'DCListName' in span['class']:
				event.name = span.text.strip()
				for a_tag in span.findAll('a', href=True):
					event.url = a_tag['href']
			if event.name in event_name_list:
				# checks to see if the event name already exists in the instance list
				# If it does, it skips it
				break
				# TKTK add state and bands to the instances
				# these items are listed in the dancecal website, and not on swingplanit
			else:
				# This means the event does not already exist in the instance list
				# and will be added
				if 'DCEventInfoWhere' in span['class']:
					location_list = span.text.replace(':',',').split(',')
					if len(location_list) == 3:
						event.country = location_list[2].strip()
						event.city = location_list[1].strip()
					if len(location_list) == 4:
						event.country = location_list[3].strip()
						event.state = location_list[2].strip()
						event.city = location_list[1].strip()
				if 'DCEventInfoDances' in span['class']:
					event.dance_styles = span.text.split(': ')[1].lower().strip()
				if 'DCEventInfoTeachers' in span['class']:
					event.teachers = str(span).replace('<br/>', '$').replace(':', '$').replace('</i>', '$').replace('|', 'and').split('$')[1:-1]
				if 'DCEventInfoDesc' in span['class']:
					event.details = span.text.strip()
				if 'DCEventInfoBands' in span['class']:
					event.bands = span.text.split(':')[1].strip()
		event_list.append(event)
	return event_list
				# print('Name: {}, Location: {}, {}, Dances: {}, Dates: {}'.format(event.name, event.city, event.country, event.dance_styles, event.start_date))





# Scrape from swingplanit.com
scrape_swing_planit()


# scrape from dancecal.com
scrape_dance_cal()
import pdb; pdb.set_trace()
