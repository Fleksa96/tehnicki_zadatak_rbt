# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json
import re

import requests
from bs4 import BeautifulSoup
from user import User


def getData(sport, counter, table_data_tr):
    table_data_td = []
    while (counter < len(table_data_tr) and table_data_tr[counter].find('a') != None):
        tr = table_data_tr[counter]
        u = User()
        u.sport = sport
        u.name = ""
        u.position = ""
        u.phone = ""
        u.email = ""

        if tr.find('th'):
            u.name = tr.th.text.replace("\n", "")

        tr = table_data_tr[counter].find_all('td')
        for td in tr:
            text = td.text.replace("\n", "").replace("\r", "").replace("\t", "").strip()
            if(td.find('a')!=None and td.find('span') == None):
                if re.match('^([A-Za-z\s]+)$', text):
                    u.name = text
                    continue
                if re.match('^(@[a-z.]+)$', text):
                    u.email = text
                elif td.a.get('href') != None:
                    x = td.a.get('href').split(':')
                    u.email = x[-1]
                continue
            else:

                if re.match('^([A-Za-z\s,\']+)$', text):
                    u.position = text
                    continue
            if re.match('^([0-9()\s-]+)$', text) or td.find('span') != None:
                if(td.find('span') != None):
                    u.phone = td.span.text.replace("\n", "").replace("\r", "").replace("\t", "")
                else:
                    u.phone = text
                continue

        table_data_td.append(u.__dict__)
        counter += 1

    return table_data_td



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--url')
    parser.add_argument('--sport')
    args = parser.parse_args()

    url = args.url
    sport = args.sport



    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all('table')

    users = []

    for table in tables:
        table_data_tr = table.find_all('tr')


        counter = 0

        for tr in table_data_tr:
            counter += 1
            if tr.find('a') == None:
                if (tr.find('th') != None and tr.th.text == sport):
                    users = getData(sport, counter, table_data_tr)
                elif tr.find('td') != None and tr.td.text == sport:
                    users = getData(sport, counter, table_data_tr)



    jsonString = json.dumps(users)

    print(jsonString)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
