# https://github.com/serv0id/sarajevo-scraper

import sys
import config
from typing import Union
import requests, json
import csv

NoneType = type(None)

class CsvScraper(object):
	def __init__(self, movie_id: int):
		self.movie_id = movie_id
		self.session = requests.Session()

	def get_details(self) -> dict:
		'''
		Returns a dict from the data fetched by the 
		sff API.
		'''
		s = self.session.get(url=config.INFO_URL.format(self.movie_id))
		s_info = s.json()

		parse_field = lambda field: s_info[field] if s_info.get(field) is not None else " "
		
		parsed_dict = {
			"URL": f"https://tickets.sff.ba/films/{self.movie_id}",
			"Title": parse_field("title"),
			"Year": parse_field("completionYear"),
			"Countries": parse_field("countriesCsv"),
			"Runtime": parse_field("runtimeHumanReadable"),
			"Languages": parse_field("languagesCsv"),
			"Poster URL": parse_field("poster"),
			"Screening Date": self.get_screening_details(),
			"Category": parse_field("filmProgrammes")
			}

		if s_info.get("filmCrew") is not None:
			for field in s_info["filmCrew"]:
				if field["crewTypeName"] == "director":
					parsed_dict["Director(s)"] = field["crewMembersCsv"]
				elif field["crewTypeName"] == "writer":
					parsed_dict["Writer(s)"] = field["crewMembersCsv"]

		return parsed_dict

	def get_screening_details(self) -> Union[str, NoneType]:
		'''
		Retrieve screening date from the screening 
		endpoint.
		'''
		s = self.session.get(url=config.SCREENING_URL.format(self.movie_id)).json()

		try:
			date = s["data"][0]["startTime"].split('T')[0]
		except:
			print("[-] Date not found!")
			date = None

		return date


def main() -> None:
	# check for arg sanity
	if len(sys.argv) < 2:
		print("[-] Kindly pass the movie id as an argument!")
		sys.exit(0)
	if not '-' in sys.argv[1]:
		print("[-] Kindly provide a range of movie ids!")
		sys.exit(0)

	FIELD_HEADINGS = ["URL", "Title", "Year", "Countries", "Runtime", "Languages",
					  "Poster URL", "Screening Date", "Category", "Director(s)", "Writer(s)"]																
	
	DATA_LIST = []
	
	for i in range(int(sys.argv[1].split('-')[0]), int(sys.argv[1].split('-')[1]) + 1):
		print(f"[+] Getting ID: {i}")
		csvscraper = CsvScraper(i)
		DATA_LIST.append(csvscraper.get_details())

	with open(config.CSV_FILE, 'w', encoding="utf-16") as f:
		writer = csv.DictWriter(f, fieldnames=FIELD_HEADINGS, dialect="excel-tab")
		writer.writeheader()

		for data in DATA_LIST:
			writer.writerow(data)
	print("[+] File written successfully!")

if __name__ == "__main__":
	main()
