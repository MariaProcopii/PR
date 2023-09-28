import json
import requests
from bs4 import BeautifulSoup


url = 'https://999.md//ro/84338236'
def get_info(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    description_items = soup.select(".adPage__content__features__col.grid_9.suffix_1 li")
    description_ad_info = soup.select(".adPage__content__features__col.grid_7.suffix_1 li")

    title = soup.title.string
    location = soup.select(".adPage__aside__address-feature__text")[0].getText().strip()
    price = soup.select(".adPage__content__price-feature__prices__price__value")[0].getText() + "€"

    description = {
        "Title": title,
        "Location": location,
        "Price": price,
        "Description": {item.select(".adPage__content__features__key")[0].getText():
                        item.select(".adPage__content__features__value")[0].getText().strip()
                        for item in description_items},
        "Additional": [i.getText() for i in description_ad_info]
    }

    return json.dumps(description, indent=4, ensure_ascii=False)

info = get_info(url)
print(info)