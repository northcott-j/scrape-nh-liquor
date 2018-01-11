"""
Process:
0. Open file (use command prompt file name) and write headers
1. For every item on a page on http://www.liquorandwineoutlets.com/products
	1a. Create Booze
	1b. Scrape
	1c. Export as dict
	1d. Write to row
2. Go to next page
3. Repeat until length of tr is 1
4. Exit
"""
import bs4
import csv
import datetime
import requests
import urllib
import sys
from src.Booze import Booze

class InventoryFile:
	def __init__(self):
		today = datetime.date.today()
		print "Opening inventory file {0}...".format("si{0}.csv".format(today.strftime("%y%m%d")))
		open_csv = urllib.urlopen("https://ice.liquor.nh.gov/bis/common/si{0}.csv".format(today.strftime("%y%m%d")))
		print "Inventory has been loaded!"
		self.si = [r for r in csv.reader(open_csv)]

	def get_stores(self):
		stores = set()
		skipped_head = False
		for r in self.si:
			if not skipped_head:
				skipped_head = True
			else:
				stores.add("{0} (#{1})".format(r[1].title(), r[0]))
		return stores

	def get_items(self):
		skipped_head = False
		items = set()
		for r in self.si:
			if not skipped_head:
				skipped_head = True
			else:
				items.add(int(r[2]))
		return items

if __name__ == "__main__":
	inv = InventoryFile()
	headers = ["id",
			"name",
			"description",
			"size",
			"price",
			"sale_price",
			"sale_ends",
			"type",
			"category",
			"sub_category",
			"pic_url",
			"recommended",
			"_hash"] + [i for i in inv.get_stores()]

	save_file = sys.argv[1]
	with open(save_file, 'w') as save:
		writer = csv.writer(save)
		writer.writerow(headers)
		for item in inv.get_items():
			try:
				b = Booze(int(item))
				b.scrape()
				b_dict = b.export_as_dict()
				writer.writerow([b_dict.get(h, '') for h in headers])
			except:
				print "Real weird error for item: {0}".format(item)

