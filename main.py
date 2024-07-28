from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from curl_cffi import requests

from json import loads
from time import sleep

from card import Card


def get_driver(options: webdriver.ChromeOptions) -> webdriver.Chrome:
    driver = webdriver.Chrome(r'C:\Users\Владислав\JT PycharmProjects\Ozon parser\chromedriver.exe', options=options)
    stealth(
        driver,
        languages=['en-US', 'en'],
        vendor='Google Inc.',
        platform='Win32',
        webgl_vendor='Intel Inc.',
        renderer='Intel Iris OpenGL Engine',
        fix_hairline=True
    )
    driver.maximize_window()

    return driver


def get_driver_options() -> webdriver.ChromeOptions:
    options: webdriver.ChromeOptions = webdriver.ChromeOptions()
    options.add_argument('chrome.switches --disable-extensions')

    return options


def get_cards(driver: webdriver.Chrome, url: str) -> list:
    all_cards = list()

    driver.get(url)
    scroll_page(driver, 50)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    content = soup.find('div', {'class': 'container'})
    content = content.findChildren(recursive=False)[-1].find('div')
    content = content.findChildren(recursive=False)
    content = [item for item in content if 'freshIsland' in str(item)][-1]
    content = content.find('div').find('div').find('div')
    content = content.findChildren(recursive=False)

    for layer in content:
        layer = layer.find("div")
        cards = layer.findChildren(recursive=False)

        cards_in_layer = list()
        for card in cards:
            card = card.findChildren(recursive=False)

            card_name = card[2].find('span', {'class': 'tsBody500Medium'}).contents[0]
            card_url = card[2].find('a', href=True)['href']
            product_url = url + card_url

            product_id, full_name, description, price, rating, rating_counter, image_url = get_card(card_url)
            card_info = {product_id: {'short_name': card_name,
                                      'full_name': full_name,
                                      'description': description,
                                      'url': product_url,
                                      'rating': rating,
                                      'rating_counter': rating_counter,
                                      'price': price,
                                      'image_url': image_url
                                      }
                         }
            cards_in_layer.append(card_info)
            print(product_id)

        all_cards.extend(cards_in_layer)

    return all_cards


def get_card(card_url: str) -> Card:
    """
    the function gets parameters of good on shop via API
    :param card_url:
    :return card:
    """
    session = requests.Session()

    data = session.get('https://ozon.ru/api/composer-api.bx/page/json/v2?=url' + card_url)
    data = loads(data.content.decode())

    # if data['layout'][0]['component'] == 'userAdultModal':

    card = Card(
        id=loads(data['seo']['script'][0]['innerHTML'])['sku'],
        url=card_url,
        title=data['seo']['title'],
        description=loads(data['seo']['script'][0]['innerHTML'])['description'],
        price=loads(data['seo']['script'][0]['innerHTML'])['price'] + \
              ' ' + loads(data['seo']['script'][0]['innerHTML'])['priceCurrency'],
        rating_value=loads(data['seo']['script'][0]['innerHTML'])['ratingValue'],
        rating_counter=loads(data['seo']['script'][0]['innerHTML'])['reviewCount'],
        image_url=loads(data['seo']['script'][0]['innerHTML'])['image']
    )

    return card


def scroll_page(driver: webdriver.Chrome, deep: int) -> None:
    """
    the function scrolls down the html page
    :param driver:
    :param deep:
    :return:
    """
    for _ in range(deep):
        driver.execute_script('window.scrollBy(0, 500)')
        sleep(0.1)


def main() -> None:
    url = 'https://ozon.ru/'
    query = 'авто+аксессуары'
    api_query = f'{url}/search/?text={query}&from_global=true'

    try:
        options = get_driver_options()
    except Exception as ex:
        print(f'Options are not prepared: {ex}')
        exit(1)

    try:
        driver = get_driver(options)
    except Exception as ex:
        print(f'Driver is not prepared: {ex}')
        exit(1)

    try:
        cards = get_cards(driver, url)
        print(f'Found {len(cards)} cards')
    except Exception as ex:
        print(f'Goods are not found: {ex}')
        exit(1)

    try:
        search_cards = get_search_cards(driver, api_query)
        print(f'Found {len(search_cards)} cards using query: {query}')
    except Exception as ex:
        print(f'Goods are not found: {ex}')
        exit(1)

    driver.quit()


if __name__ == '__main__':
    main()
