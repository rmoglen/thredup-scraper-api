import requests, re, time, random, argparse, os, sys, csv, glob
from bs4 import BeautifulSoup
import pandas as pd
from alive_progress import alive_bar
import pyperclip

# --------------------------------------------------
""" Define inputs """

#Jeans
url1 = "https://www.thredup.com/women/jeans/straight-leg-jeans?chars_inseam_in=%5B24%3A26%5D%2C%5B27%3A29%5D%2C%5B30%3A32%5D&chars_jean_wash=light%20wash%2Cmedium%20wash&chars_waist=high%20rise&department_tags=women&search_tags=women-jeans%2Cwomen-jeans-straight-leg%2Cwomen-jeans-skinny%2Cwomen-jeans-boyfriend&state=listed&price=0%2C70"
# url1= "https://www.thredup.com/women?department_tags=women"
pages = 2
file_name = "jeans"


# --------------------------------------------------
def main():

	url = url1 + '&page='
	product_list = []
	url_front = 'https://www.thredup.com'

	# Everytime range increases, items increase by 50.
	for page_number in range(1, pages + 1):
		url_page = ((url) + str(page_number))

		# Parse HTML and pull all href links
		response = requests.get(url_page)
		main_page_items = BeautifulSoup(response.text, 'html.parser')
		grid_products = main_page_items.findAll(
			'div', {'class': 'grid-item'})
		for i in grid_products:
			try:
				product = i.find('a', {
					'class': 'WCdF1-WeVI0oEKb0AIa4c'
					}).get('href')
				product_list.append(url_front + product)
			except:
				print("URL Retrival Error")

	image = []
	description = []
	materials = []
	size = []
	measurements = []
	price = []
	brand = []

	# with alive_bar(len(product_list)) as bar:
	progress=0
	for link in product_list:
		print(link)
		print("Progress: ", str(progress),"/",str(len(product_list)))
		response = requests.get(link)
		product_page_soupified = BeautifulSoup(response.text,
											   'html.parser')

		#Product Image Link
		image_search = product_page_soupified.find(
			'a', {'class': '_YFsbsE3S64aEw-MiDk2C'}).get('href')
		image.append(image_search)

		#Extract listed details
		listed_details = product_page_soupified.findAll(
			 'ul', {'class': 'list-disc'})

		#Product Size and Measurements
		measurement_size_search = listed_details[1]
		measurement_size_search = str(measurement_size_search).split("<button")[0:2]

		size.append(measurement_size_search[0].split("<li>")[1].split("</li>")[0])
		try:
			measurements.append(measurement_size_search[1].split("<li>")[1].split("</li>")[0])
		except:
			#append size if measurements doesn't work
			measurements.append(measurement_size_search[0].split("<li>")[1].split("</li>")[0])

		#Description
		description_list=[]
		description_search = listed_details[0].findAll('li')
		for i in description_search:
			description_list.append(i.text)
		description.append(description_list)

		#Brand
		brand_search = product_page_soupified.find(
			'a', {'class': 'ui-link u-text-20'}).get('title')
		brand.append(brand_search)

		#Materials
		materials_search = product_page_soupified.findAll(
			'div', {'class': '_2pmDWTgK3W9qnhtkNz7uFZ'})
		for i in materials_search:
			if "Materials" in str(i):
				materials.append(str(i).split("<p>")[1].split("</p>")[0])

		#Price
		price_search=str(product_page_soupified)
		price_search=price_search.split("\",\"priceCurrency\":\"USD\"")[1].split("price\":\"")[1]
		price.append(price_search)

		#For Debugging
		# print("Size:", size)
		# print("Measurements: ", measurements)
		# print("Brand: ", brand)
		# print("Materials: ", materials)
		# print("Description: ", description)
		# print ("Price: ", price)
		
		progress += 1

	basic_scrape = pd.DataFrame({
				'Link': product_list,
				'Image_Link': image,
				# 'Category_Type': category_type,
				'Description': description,
				'Materials': materials,
				'Size': size,
				'Measurements': measurements,
				'Price': price,
				'Brand': brand
			})

	basic_scrape.to_csv(
				r'./../data/test_runs/{file_name}.csv'
				.format(file_name=file_name), index=False, header=True)



# --------------------------------------------------
if __name__ == '__main__':
	main()
