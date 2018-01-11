"""
Process:
1. Takes two filenames from command prompt (old, new)
2. Creates file that has only items with diff hash between old and new/doesn't appear
"""
import csv
import sys

if __name__ == "__main__":
	old = sys.argv[1]
	new = sys.argv[2]
	result = sys.argv[3]
	diff = {}
	with open(old, 'r') as old_file:
		old_reader = csv.reader(old_file)
		old_items = {r[0]: r for r in old_reader}

	with open(new, 'r') as new_file:
		new_reader = csv.reader(new_file)
		new_items = {r[0]: r for r in new_reader}

	with open(result, 'w') as results:
		writer = csv.writer(results)
		writer.writerow(new_items['id'])

	for b_id in new_items:
		if b_id == 'id':
			continue
		row = new_items[b_id]
		old_row = old_items.get(b_id, [])
		if not old_row or row[12] != old_row[12]:
			writer.writerow(row)
	
	# TODO :: Support when an item is discontinued 
