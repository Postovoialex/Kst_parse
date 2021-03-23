from bs4 import BeautifulSoup
import lxml
import requests
import time
from datetime import datetime
import csv
import os

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Cookie": "lang=ru"
}
links = []
brand_list = ['https://kasta.ua/brand/TOTALFIT/']
data = []
product_info = {}
open('product_list.html', 'w')
key_list = ['URL', 'Name', 'Description']
start_time = datetime.now()
received_data = 0

print('start process - scrapping')
print('working process - get product link from brands link')
for brand_link in brand_list:
    offset = 24
    while True:
        q = requests.get(url=f'{brand_link}?offset={offset}', headers=headers)
        q.encoding = 'utf-8'
        src = q.text
        soup = BeautifulSoup(src, 'lxml')
        find_img_with_goods_links = soup.findAll('div', attrs={'class': "product__img"})

        for link in find_img_with_goods_links:
            link = link.a['href']
            links.append(link)

        print(f'links received - {len(links)}')

        if q.status_code == 200:
            offset = offset + 24
        else:
            break

    with open('product_links.html', 'w') as file:
        for link in links:
            file.write(f'https://kasta.ua{link}\n')
print('get product link from brands link - DONE')

print('working process - get product info from product links')
with open('product_links.html', 'r') as file:
    for line in file:
        product_url = line.rstrip('\n')
        get_product_page = requests.get(url=product_url, headers=headers)
        get_product_page.encoding = 'utf-8'
        get_product_text = get_product_page.text
        soup = BeautifulSoup(get_product_text, 'lxml')

        print(product_url)
        try:
            product_name = soup.find('h1', attrs={'class': 'pd__header-product__name'}).text
        except AttributeError:
            print('ERROR, please wait')
            time.sleep(10)
            try:
                product_name = soup.find('h1', attrs={'class': 'pd__header-product__name'}).text
                print('Error fixed, continue')
            except AttributeError:
                print('ERROR do not fixed. Product name not find')
                product_name = 'not find'

        try:
            product_description = soup.find('span', attrs={'class': 'pd_prop-val'}).text
        except AttributeError:
            product_description = 'None'
        product_character_name_list = soup.find_all('div', attrs={'class': 'pd_prop-title'})
        product_character_info_list = soup.find_all('div', attrs={"class": 'pd_prop-val'})

        product_info['URL'] = product_url
        product_info['Name'] = product_name
        for index in range(len(product_character_name_list)):
            product_info[product_character_name_list[index].text] = product_character_info_list[index].text
            key_list.append(product_character_name_list[index].text)
        product_info['Description'] = product_description

        with open('product_list.html', 'a') as file:
            file.write(f'{str(product_info)}\n')

        received_data += 1
        print(f"received data = {received_data}/{len(links)}")

        unique_list_key = set(key_list)
        key_list = list(unique_list_key)
        product_info.clear()
print('get product info from product links - DONE')

print('working process - create finish file')
with open('product_list.html', 'r') as file:
    for line in file:
        product_data_str = line.rstrip('\n')
        product_data_dict = eval(product_data_str)
        for key in product_data_dict:
            key_list.append(key)
unique_list_key = set(key_list)
key_list = list(unique_list_key)
key_list.sort()

with open('product_list.html', 'r') as file:
    for line in file:
        product_data_str = line.rstrip('\n')
        product_data_dict = eval(product_data_str)
        for key in key_list:
            if key in product_data_dict:
                pass
            else:
                product_data_dict[key] = 'None'

        for key in key_list:
            data_key = product_data_dict[key]
            data.append(data_key)
        with open('data_list.html', 'a') as f:
            f.write(str(f'{data}\n'))

        data.clear()

with open("Result_parse_data.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
    file_writer.writerow(key_list)
    with open('data_list.html', 'r') as file:
        for line in file:
            data = line.rstrip('\n')
            x = data.split('\', \'')
            file_writer.writerow(x)

os.remove('data_list.html')
os.remove('product_list.html')
os.remove('product_links.html')
print('create finish file - DONE')

print(f'Done! process worked - {datetime.now() - start_time}')
