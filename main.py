# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json
import re
import constant

import requests
from bs4 import BeautifulSoup
from user import User

#sport, counter - from which tr to start collecting users, table_data_tr - all tr-s from table
def getData(sport, counter, table_data_tr):
    table_data_td = [] #this is for collecting users
    while (counter < len(table_data_tr) and table_data_tr[counter].find('a') != None):
        #if i got to the end of table i jump of while, if there is no a tag in tr it means i encountered the
        #next tag in table
        tr = table_data_tr[counter]
        u = User()

        #i did this only to have correct output in cmd
        u.sport = sport.lower()
        u.name = ""
        u.position = ""
        u.phone = ""
        u.email = ""

        #on one test page name is given in th tag, so this will get name from there
        #because down i am just getting td-s from tr
        if tr.find('th'):
            u.name = tr.th.text.replace("\n", "")

        tr = table_data_tr[counter].find_all('td')
        for td in tr:
            text = td.text.replace("\n", "").replace("\r", "").replace("\t", "").strip()
            #names and email is given in a tag
            if(td.find('a')!=None and td.find('span') == None):
                if re.match(constant.REGEX_NAME, text):
                    u.name = text
                    continue
                if re.match(constant.REGEX_EMAIL, text):
                    u.email = text
                elif td.a.get('href') != None:
                    x = td.a.get('href').split(':')
                    u.email = x[-1]
                continue
            else:

                if re.match(constant.REGEX_POSITION, text):
                    u.position = text
                    continue
            #i did not put this if in the else branch, because on one site there is phone
            #given inside a tag and span tag, so this logic below covers that case
            if re.match(constant.REGEX_PHONE, text) or td.find('span') != None:
                if(td.find('span') != None):
                    u.phone = td.span.text.replace("\n", "").replace("\r", "").replace("\t", "")
                else:
                    u.phone = text
                continue
        #adding to array of users
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

    #collecting named arguments with ArgumentParser

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}

    s = requests.Session()
    s.headers.update(headers)
    page = s.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all('table')

    users = []

    #one site has multiple tables
    for table in tables:

        #as soon as i get users array, i don't need to go through other tables
        #and i just jump out of for loop
        if users:
            break

        table_data_tr = table.find_all('tr')


        counter = 0

        for tr in table_data_tr:
            counter += 1
            #tr that does not have a tag is where i check for sport and start collecting items if
            #that is the sport that i am looking for
            if tr.find('a') == None:
                if (tr.find('th') != None and tr.th.text.lower() == sport.lower()):
                    #on one site first column is th not td tag
                    users = getData(sport, counter, table_data_tr)
                    # as soon as i get users array, i don't need to go through other tables
                    # and i just jump out of for loop
                    break
                elif tr.find('td') != None and tr.td.text.lower() == sport.lower():
                    users = getData(sport, counter, table_data_tr)
                    # as soon as i get users array, i don't need to go through other tables
                    # and i just jump out of for loop
                    break


    #turning array of users to Json format
    jsonString = json.dumps(users)

    print(jsonString)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
