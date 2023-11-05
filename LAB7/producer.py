#!/usr/bin/python3.10

import json
import requests
import bs4
import pika


html = "https://m.999.md/ro/list/real-estate/apartments-and-rooms?applied=1&o_30_241=902&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page={}"
links = []

def scraper(html, max_page_num = 99, start_page = 1):

    if start_page > max_page_num:
        return

    res = requests.get(html.format(start_page))

    if res.status_code == 200:
        soup = bs4.BeautifulSoup(res.text, "lxml")

        for child in soup.select(".block-items__item__title"):
            if "/booster/" not in child.get("href"):
                links.append("https://999.md/" + child.get("href"))

        scraper(html, max_page_num, start_page + 1)

def get_info(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")

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

def publish_message_to_queue(message):
    channel.basic_publish(exchange='', routing_key='queue', body=message)
    print(f" [*] Sent {message}")

if __name__=="__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='queue')

    scraper(html, 1)
    for link in links:
        info = get_info(link)
        publish_message_to_queue(info)

    connection.close()