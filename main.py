# https://github.com/serv0id/sarajevo-scraper

import sys
import config
import requests, json
import csv

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
		
		parsed_dict = {
			"URL": f"https://tickets.sff.ba/films/{self.movie_id}",
			"Title": s_info["title"],
			"Year": s_info["completionYear"],
			"Countries": s_info["countriesCsv"],
			"Runtime": s_info["runtimeHumanReadable"],
			"Languages": s_info["languagesCsv"],
			"Poster URL": s_info["poster"] if s_info.get("poster") is not None else "",
			"Screening Date": self.get_screening_details()
			}

		for field in s_info["filmCrew"]:
			if field["crewTypeName"] == "director":
				parsed_dict["Director(s)"] = field["crewMembersCsv"]
			elif field["crewTypeName"] == "writer":
				parsed_dict["Writer(s)"] = field["crewMembersCsv"]

		return parsed_dict

	def get_screening_details(self) -> str:
		s = self.session.get(url=config.SCREENING_URL.format(self.movie_id)).json()

		return s["data"][0]["startTime"].split('T')[0]


def main() -> None:
	# check for arg sanity
	if len(sys.argv) < 2:
		print("[-] Kindly pass the movie id as an argument!")
		sys.exit(0)
	if not '-' in sys.argv[1]:
		print("[-] Kindly provide a range of movie ids!")
		sys.exit(0)

	FIELD_HEADINGS = ["URL", "Title", "Year", "Countries", "Runtime", "Languages",
					  "Poster URL", "Screening Date", "Director(s)", "Writer(s)"]																
	
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
