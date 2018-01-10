""" Class to get an item from NH Liquor Store's website """
import bs4
import hashlib
import json
import requests
import urllib

class Booze:
	default_imgs = ['/assets/images/products/wine_silo.jpg', '/assets/images/products/spirit_silo.jpg']

	def __init__(self, id):
		self.item = id
		self._hash = ''
		self.product_page = None
		self.name = ''
		self.desc = ''
		self.size = ''
		self.price = 0.00
		self.sale_price = -1.00
		self.sale_ends = ''
		self.type = ''
		self.category = ''
		self.sub_category = ''
		self.pic_url = ''
		self.store_inv = {}
		self.rec_items = []

	def scrape(self):
		scrapers = [self.set_product_page, self.set_name, self.set_desc, self.set_size, self.set_price, self.set_sale_price,
					self.set_sale_ends, self.set_type, self.set_category, self.set_sub_category, self.set_pic_url,
					self.set_store_inv, self.set_rec_items, self.set_hash]
		for s in scrapers:
			print "Running {0} for {1}...".format(s.__name__, self.item)
			try:
				s()
			except:
				print "FAILED {0} for {1}!!!!".format(s.__name__, self.item)
		self.product_page = None

	def export_as_dict():
		"""
		Exports needed fields as a dictionary
		:return: Dict
		"""
		d = {
			"id": self.item,
			"name": self.name,
			"description": self.description,
			"size": self.size,
			"price": self.price,
			"sale_price": self.sale_price,
			"sale_ends": self.sale_ends,
			"type": self.type,
			"category": self.category,
			"sub_category": self.sub_category,
			"pic_url": self.pic_url,
			"recommended": self.rec_items
			"_hash": self._hash
		}
		d.update(self.store_inv)
		return d

	def hash(self):
		"""
		Creates a hash string to check equality
		:return: String
		"""
		def dict_hash(d):
			"""
			Creates a consistent hash of a dictionary
			:return: Hash String
			"""
			return hashlib.md5(str(sorted(d.items()))).hexdigest()

		def array_hash(a):
			"""
			Creates a consistent hash of an array
			:return: Hash String
			"""
			return hashlib.md5(str(a)).hexdigest()

		return hashlib.md5("{0}-{1}-{2}-{3}-{4}-{5}-{6}-{7}-{8}-{9}-{10}-{11}".format(self.name, self.desc, 
			self.size, self.price, self.sale_price, self.type, self.category, dict_hash(self.store_inv), 
			array_hash(self.rec_items), self.pic_url, self.sub_category, self.sale_ends)).hexdigest()

	def set_hash(self):
		"""
		Sets the unique hash
		:mutate self._hash
		:return: Hash String
		"""
		self._hash = self.hash()
		return self._hash

	def product_page_url(self):
		"""
		Creates the URL to lookup a product on website
		:return: String
		"""
		return "http://www.liquorandwineoutlets.com/products/detail/{0}".format(self.item)

	def google_img_search_url(self):
		"""
		Makes a URL to do a google img search
		:return: String
		"""
		return "https://www.google.com/search?q={0}+{1}&source=lnms&tbm=isch".format(self.name.upper().replace(' ', '+'), self.size)

	def set_product_page(self):
		"""
		Sets the product_page to a bs4'd item
		:mutates self.product_page
		:return: BS4
		"""
		r = requests.get(self.product_page_url())
		s = bs4.BeautifulSoup(r.content, 'html.parser')
		self.product_page = s
		return s

	def get_product_field(self, f):
		"""
		Uses a function to get a field
		:param f: a function to get a field from bs4 page
		:return: the return value of f
		"""
		if not self.product_page:
			self.set_product_page()
		return f()

	def set_name(self):
		"""
		Gets the name of the Booze
		:mutates: self.name
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				val = art.find('h1').text
			return val

		self.name = self.get_product_field(retrieve)
		return self.name

	def set_desc(self):
		"""
		Gets the desc of the Booze
		:mutates: self.desc
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				p_text = art.find('p').text
				if "Size:" not in p_text:
					val = p_text
			return val

		self.desc = self.get_product_field(retrieve)
		return self.desc

	def set_size(self):
		"""
		Gets the size of the Booze
		:mutates: self.size
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				div = art.find('div')
				if div:
					p = div.find('p')
					if p:
						val = p.text.split('Size:')[1].strip()
			return val

		self.size = self.get_product_field(retrieve)
		return self.size

	def set_price(self):
		"""
		Gets the price of the Booze
		:mutates: self.price
		:return: float
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = 0.00
			if art:
				div = art.find('div')
				if div:
					val = float(div.find('p', class_="big red").text.split("$")[1].strip())
					sale = div.find('div', class_="col col_1")
					if sale and "Regular Price" in sale.text:
						val = float(sale.text.strip().split("\n")[0].replace("Regular Price: $", '').strip())
			return val

		self.price = self.get_product_field(retrieve)
		return self.price

	def set_sale_price(self):
		"""
		Gets the sale price of the Booze
		:mutates: self.sale_price
		:return: float
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = -1.00
			if art:
				div = art.find('div')
				if div:
					pos_sale_price = float(div.find('p', class_="big red").text.split("$")[1].strip())
					sale = div.find('div', class_="col col_1")
					if sale and 'Regular Price' in sale.text:
						val = pos_sale_price
			return val

		self.sale_price = self.get_product_field(retrieve)
		return self.sale_price

	def set_sale_ends(self):
		"""
		Gets the sale end date of the Booze
		:mutates: self.sale_ends
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				div = art.find('div')
				if div:
					sale = div.find('div', class_="col col_1")
					if sale and 'Sale Ends' in sale.text:
						val = sale.text.split("Sale Ends:")[1].strip()
			return val

		self.sale_ends = self.get_product_field(retrieve)
		return self.sale_ends

	def set_type(self):
		"""
		Gets the type of the Booze
		:mutates: self.type
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				div_2_col = art.find('div', class_="cols cols_2")
				if div_2_col:
					cats = div_2_col.find('div', class_="col col_2")
				else:
					cats = art.find('div', class_="hr").find_next_sibling("p")
				if cats and "Type:" in cats.text:
					val = cats.text.split("Type:")[1].split('\n')[0].strip()
			return val

		self.type = self.get_product_field(retrieve)
		return self.type

	def set_category(self):
		"""
		Gets the category of the Booze
		:mutates: self.category
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				div_2_col = art.find('div', class_="cols cols_2")
				if div_2_col:
					cats = div_2_col.find('div', class_="col col_2")
				else:
					cats = art.find('div', class_="hr").find_next_sibling("p")
				if cats and "Category:" in cats.text:
					val = cats.text.split("Category:")[1].split('\n')[0].strip()
			return val

		self.category = self.get_product_field(retrieve)
		return self.category

	def set_sub_category(self):
		"""
		Gets the sub category of the Booze
		:mutates: self.sub_category
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = ''
			if art:
				div_2_col = art.find('div', class_="cols cols_2")
				if div_2_col:
					cats = div_2_col.find('div', class_="col col_2")
				else:
					cats = art.find('div', class_="hr").find_next_sibling("p")
				if cats and "Sub-Category:" in cats.text:
					val = cats.text.split("Sub-Category:")[1].split('\n')[0].strip()
			return val

		self.sub_category = self.get_product_field(retrieve)
		return self.sub_category

	def get_google_img_url(self):
		val = ''
		header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
		r = requests.get(self.google_img_search_url(), headers=header)
		google = bs4.BeautifulSoup(r.content, 'html.parser')
		a = google.find("div",{"class":"rg_meta"})
		link , t = json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
		if link:
			val = link
		return val

	def set_pic_url(self):
		"""
		Gets the url to the pitcture of the Booze
		:mutates: self.pic_url
		:return: String
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			side = self.product_page.find('aside')
			val = ''
			if side:
				img = side.find('img')
				if img and img["src"] in self.default_imgs:
					val = self.get_google_img_url()
				else:
					val = img["src"]
			return val

		self.pic_url = self.get_product_field(retrieve)
		return self.pic_url

	def set_store_inv(self):
		"""
		Gets the inventory of each store for the Booze
		:mutates: self.store_inv
		:return: Dict
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			art = self.product_page.find('article')
			val = {}
			if art:
				table = art.find('table')
				if table:
					tb = table.find('tbody')
					trs = tb.find_all('tr')
					for tr in trs:
						tds = tr.find_all('td')
						store_name = tds[0].text.split(',')[0].strip()
						inv = int(tds[1].text.strip())
						val[store_name] = inv
					
			return val

		self.store_inv = self.get_product_field(retrieve)
		return self.store_inv

	def set_rec_items(self):
		"""
		Gets the inventory of each recommended item for the Booze
		:mutates: self.rec_items
		:return: Array
		"""
		def retrieve():
			"""
			Gets the field
			:return: field value
			"""
			side = self.product_page.find('aside')
			val = []
			if side:
				recs = side.find_all('div', class_="sep")
				if recs:
					for r in recs:
						a = r.find('a')
						if a:
							val.append(int(a['href'].split('detail/')[1].split('/')[0]))
			return val

		self.rec_items = self.get_product_field(retrieve)
		return self.rec_items
