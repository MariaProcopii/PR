import requests
import bs4


html = "https://m.999.md/ro/list/real-estate/apartments-and-rooms?applied=1&o_30_241=902&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page={}"

links = []
def scraper(html, maxPages, start_page = 1):

    if start_page > maxPages:
        return

    res = requests.get(html.format(start_page))

    if res.status_code == 200:
        soup = bs4.BeautifulSoup(res.text, "lxml")

        for child in soup.select(".block-items__item__title"):
            if "/booster/" not in child.get("href"):
                links.append("https://999.md/" + child.get("href"))

        scraper(html, maxPages, start_page + 1)


scraper(html, 2, 1)

print(links)