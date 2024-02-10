import requests
import json
import csv
import pycountry

import time


class ShortWire(object):
    def __init__(self, film_id: int):
        self.base_url = "https://apifront.shortfilmwire.com/DataServiceRestFull.svc"
        self.session = requests.Session()
        self.out_file = f"{int(time.time())}_dump.csv"
        self.id = film_id

        self.session.headers.update({
            "Authorization": "$_$2fEYWdfaJCtiU57VkC9dVOYvx1Q9TKAeIEw$_$2fy6S1QrIbPRVqe87bmMQ$_$3d$_$3d"
        })

    def get_synopsis(self) -> str:
        s = self.session.get(url=self.base_url + f"/film/{self.id}/synopsis")
        return s.json()["m_Item1"]

    def get_metadata(self) -> dict:
        s = self.session.get(url=self.base_url + f"/film/{self.id}").json()
        return {
            "Original Title": s["TitreOriginal"],
            "International Title": s["TitreInternational"],
            "Year": s["AnneeProd"],
            "ID": s["Numero"],
            "Director": s["Realisateurs"][0],
            "Viewing copy available": s["HasCopieVisionnement"],
        }

    def start(self) -> dict:
        return {
            **self.get_metadata(),
            "Synopsis": self.get_synopsis()
        }


def main() -> None:
    with open(f"{int(time.time())}_dump.csv", 'w', newline='') as f:
        fields = ["Original Title", "International Title", "Year", "ID", "Director", "Viewing copy available", "Synopsis"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx in range(200119742, 200132168):
            shortwire = ShortWire(idx)
            writer.writerow(shortwire.start())


if __name__ == "__main__":
    main()
