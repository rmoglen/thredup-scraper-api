import requests, re, time, random, argparse, os, sys, csv, glob
from bs4 import BeautifulSoup
import pandas as pd
import pyperclip

# --------------------------------------------------
""" Define inputs """

#Jeans
url1 = "https://www.thredup.com/women/jeans/straight-leg-jeans?chars_inseam_in=%5B24%3A26%5D%2C%5B27%3A29%5D%2C%5B30%3A32%5D&chars_jean_wash=light%20wash%2Cmedium%20wash&chars_waist=high%20rise&department_tags=women&search_tags=women-jeans%2Cwomen-jeans-straight-leg%2Cwomen-jeans-skinny%2Cwomen-jeans-boyfriend&state=listed&price=0%2C70"
# url1= "https://www.thredup.com/women?department_tags=women"
pages = 27
file_name = "jeans"
refineResults= True
filterBy={"materials": {"cottonMin": 99}, 
	"measurements":{"waistMin":28,"waistMax":30, "riseMin": 11, "inseamMin":26} }

# --------------------------------------------------
def main():

	url = url1 + '&page='
	product_list = []
	url_front = 'https://www.thredup.com'

	# Everytime range increases, items increase by 50.
	for page_number in range(1, pages + 1):
		url_page = ((url) + str(page_number))

		# Parse HTML and pull all href links
		response = requests.get(url_page, timeout=30)
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

	progress=1
	for link in product_list:
		# print(link)
		print("Progress: ", str(progress),"/",str(len(product_list)))
		try:
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
				measurements.append(measurement_size_search[1].split("<li>")[1].split("</li>")[0].split(","))
			except:
				#append size if measurements doesn't work
				measurements.append(measurement_size_search[0].split("<li>")[1].split("</li>")[0].split(","))

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
					materials.append(str(i).split("<p>")[1].split("</p>")[0].split(","))

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
		except:
			print("Product Scrape Failed")

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

	if refineResults:
		linkKeep= []
		imageKeep = []
		descriptionKeep = []
		materialsKeep = []
		sizeKeep = []
		measurementsKeep = []
		priceKeep = []
		brandKeep = []

		materialsFilter=filterBy["materials"]
		measurementsFilter=filterBy["measurements"]

		for i in range(len(product_list)):
			keep=1
			# Filter by material
			for fiber in materials[i]:
				# Cotton content
				if "Cotton" in fiber and float(fiber.split("%")[0])<materialsFilter["cottonMin"]:
					keep=keep*0

				if "No Fabric Content" in fiber:
					keep=keep*0

			# Filter by measurements
			for meas in measurements[i]:
				if "Inseam" in meas and float(meas.split("\"")[0])<measurementsFilter["inseamMin"]:
					keep=keep*0

				if "Rise" in meas and float(meas.split("\"")[0])<measurementsFilter["riseMin"]:
					keep=keep*0

				if "Waist" in meas and float(meas.split("\"")[0])<measurementsFilter["waistMin"]:
					keep=keep*0

				if "Waist" in meas and float(meas.split("\"")[0])>measurementsFilter["waistMax"]:
					keep=keep*0

			if keep==1:
				linkKeep.append(product_list[i])
				imageKeep.append(image[i])
				descriptionKeep.append(description[i])
				materialsKeep.append(materials[i])
				sizeKeep.append(size[i])
				measurementsKeep.append(measurements[i])
				priceKeep.append(price[i])
				brandKeep.append(brand[i])

				basic_scrape = pd.DataFrame({
					'Link': linkKeep,
					'Image_Link': imageKeep,
					# 'Category_Type': category_type,
					'Description': descriptionKeep,
					'Materials': materialsKeep,
					'Size': sizeKeep,
					'Measurements': measurementsKeep,
					'Price': priceKeep,
					'Brand': brandKeep
				})

				basic_scrape.to_csv(
							r'./../data/test_runs/{file_name}_keep.csv'
							.format(file_name=file_name), index=False, header=True)




# --------------------------------------------------
if __name__ == '__main__':
	main()
