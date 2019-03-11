import re
import logging

from bs4 import BeautifulSoup

from weatherapp.core import config
from weatherapp.core import decorators
from weatherapp.core.abstract import WeatherProvider
from weatherapp.core.exception import WeatherProviderError


class AccuWeatherProvider(WeatherProvider):

	""" Weather provider for AccuWeather site.
	"""

	name = config.ACCU_PROVIDER_NAME
	title = config.ACCU_PROVIDER_TITLE
	logger = logging.getLogger(__name__)


	def get_name(self):
		return self.name

	def get_default_location(self):
		""" Default location name.
		"""

		return config.DEFAULT_ACCU_LOCATION_NAME

	def get_default_url(self):
		""" Default location url.
		"""

		return config.DEFAULT_ACCU_LOCATION_URL

	def get_locations_accu(self, locations_url):
	    """ Getting locations from accuweather.
	    """

	    locations_page = self.get_page_source(locations_url)
	    soup = BeautifulSoup(locations_page, 'html.parser')

	    locations = []
	    for location in soup.find_all('li', class_='drilldown cl'):
	    	url = location.find('a').attrs['href']
	    	location = location.find('em').text
	    	locations.append((location, url))
	    return locations

	def configurate(self):
	    """ Displays the list of locations for the user to select from 
	        AccuWeather.
	    """
	  
	    locations = self.get_locations_accu(config.ACCU_BROWSE_LOCATIONS)
	    while locations:
	    	for index, location in enumerate(locations):
	    		print(f'{index + 1}. {location[0]}')

	    	try:
	    		selected_index = int(input('Please select location: '))
	    	except ValueError:
	    		msg = 'Error!'
	    		if self.app.options.debug:
	    			self.logger.exception(msg)
	    		else:
	    			self.logger.error(msg)	
	    		raise WeatherProviderError(
	    	    		 'You have entered the wrong data format! \n'
	    	    		 'Repeat again, input a number.', 
	    	    		  name1=self.name).action()

	    	try:
	    		location = locations[selected_index - 1]
	    	except IndexError:
	    		msg = 'Error!'
	    		if self.app.options.debug:
	    			self.logger.exception(msg)
	    		else:
	    			self.logger.error(msg)
	    			raise WeatherProviderError(
	    	    		'You have entered a non-existent number in the '
	    		    	'list!\nRepeat again.', self.name).action()

	    	locations = self.get_locations_accu(location[1])

	    self.save_configuration(*location)

	def get_weather_info(self, page_content):
	    """ Getting the final result in tuple from site accuweather.
	    """

	    city_page = BeautifulSoup(page_content, 'html.parser')
	    weather_info = {}
	    if not self.app.options.tomorrow:
	    	current_day_selection = city_page.find\
	    	         ('li', class_=re.compile('(day|night) current first cl'))
	    	if current_day_selection:
	    		current_day_url = \
	    		                current_day_selection.find('a').attrs['href']
	    		if current_day_url:
	    			current_day_page = self.get_page_source(current_day_url)
	    			if current_day_page:
	    				current_day = BeautifulSoup(current_day_page,
                                                    'html.parser')
	    				weather_details = current_day.find('div',
                                                   attrs={'id': 'detail-now'})
	    				condition = weather_details.find('span', 
	    					                             class_='cond')
	    				if condition:
	    					weather_info['cond'] = condition.text
	    				temp = weather_details.find('span', 
	    					                         class_='large-temp')
	    				if temp:
	    					weather_info['temp'] = temp.text
	    				feal_temp = weather_details.find(
                            'span', class_='small-temp')
	    				if feal_temp:
	    					weather_info['feal_temp'] = feal_temp.text
	    else:
	    	tomorrow_day_selection = city_page.find('li',
                                                    class_='day last hv cl')
	    	if tomorrow_day_selection:
	    		tomorrow_day_url = \
	    		                tomorrow_day_selection.find('a').attrs['href']
	    		if tomorrow_day_url:
	    			tomorrow_day_page = self.get_page_source(tomorrow_day_url)
	    			if tomorrow_day_page:
	    				tomorrow_day = BeautifulSoup(tomorrow_day_page,
                                                     'html.parser')
	    				weather_details = tomorrow_day.find('div',
                                             attrs={'id': 'detail-day-night'})
	    				condition = weather_details.find('div', class_='cond')
	    				if condition:
	    					weather_info['cond'] = condition.text.strip()
	    				temp = weather_details.find('span', 
	    					                         class_='large-temp')
	    				if temp:
	    					weather_info['temp'] = temp.text
	    				feal_temp = weather_details.find('span', 
                                                         class_='realfeel')
	    				if feal_temp:
	    					weather_info['feal_temp'] = feal_temp.text

	    return weather_info