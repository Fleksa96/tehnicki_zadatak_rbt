# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import json
import re
import sys

import constant

import requests
from bs4 import BeautifulSoup
from user import User

#sport, counter - from which <tr> to start collecting users, table_data_tr - all <tr>-s from table
def getDataFromTr(sport, counter, table_data_tr):
    table_data_td = [] #this is for collecting users
    while (counter < len(table_data_tr) and table_data_tr[counter].find('a') != None):
        #if i got to the end of table i jump of while, if there is no a tag in <tr> it means i encountered the
        #next tag in table
        tr = table_data_tr[counter]
        u = User()

        #i did this only to have correct output in cmd
        u.sport = sport.lower()
        u.name = ""
        u.position = ""
        u.phone = ""
        u.email = ""

        #on one test page name is given in <th> tag, so this will get name from there
        #because down i am just getting <td>-s from <tr>
        if tr.find('th'):
            u.name = tr.th.text.replace("\n", "")

        tr = table_data_tr[counter].find_all('td')
        for td in tr:
            text = td.text.replace("\n", "").replace("\r", "").replace("\t", "").strip()
            #names and email is given in <a> tag
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
            #given inside a tag and <span> tag, so this logic below covers that case
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


def getDataFromTables(tables, sport):

    users = []

    # one site has multiple tables
    for table in tables:

        # as soon as i get users array, i don't need to go through other tables
        # and i just jump out of for loop
        if users:
            break

        table_data_tr = table.find_all('tr')

        counter = 0

        for tr in table_data_tr:
            counter += 1
            # <tr> that does not have <a> tag is where i check for sport and start collecting items if
            # that is the sport that i am looking for
            if tr.find('a') == None:
                if (tr.find('th') != None and tr.th.text.lower() == sport.lower()):
                    # on one site first column is <th> not <td> tag
                    users = getDataFromTr(sport, counter, table_data_tr)
                    # as soon as i get users array, i don't need to go through other tables
                    # and i just jump out of for loop
                    break
                elif tr.find('td') != None and tr.td.text.lower() == sport.lower():
                    users = getDataFromTr(sport, counter, table_data_tr)
                    # as soon as i get users array, i don't need to go through other tables
                    # and i just jump out of for loop
                    break
    return users

def getDataFromIframes(iframes, sport, session):
    users = []
    #searching users through tables in iframes
    for ifrm in iframes:
        if users:
            break

        if ifrm.has_attr('src'):
            width = ifrm['width']
            height = ifrm['height']
            u = ifrm['src']
            #if width or height is 0, i noticed that <iframes> had style tag
            #with css visibility: hidden so i jump to another iframe
            #if <iframe> does not have http or https in front of a link i jump to another <iframe>
            if width == 0 or height == 0 or u.find('http') == -1:
                continue
            page = session.get(u)
            soup = BeautifulSoup(page.content, 'html.parser')

            tables = soup.find_all('table')
            if tables:
                users = getDataFromTables(tables, sport)

    return users

def getTablesFromTrOptArg(soup, html_element, html_element_id, html_element_index, html_element_class):
    tables = []
    #html element is <tr>, so i get all specific <tr>s and get their table, and append in tables only unique values
    if html_element_id != None:
        temp = soup.find(html_element, attrs={'id': html_element_id})
        if temp != None and temp:
            tables.append(temp.find_previous('table'))
    elif html_element_index != None:
        temp = soup.find_all(html_element)
        if len(temp) > html_element_index:
            tables.append(temp[html_element_index].find_previous('table'))
    else:
        tr = soup.find_all(html_element, attrs={'class': html_element_class})
        if tr != None:
            for t in tr:
                table = t.find_previous('table')
                if table != None and table not in tables:
                    tables.append(table)
    return tables

def getTablesOptionalArguments(soup, html_element, html_element_id, html_element_index, html_element_class):
    tables = []
    #if html element is tr
    if html_element == 'tr':
        tables = getTablesFromTrOptArg(soup, html_element, html_element_id, html_element_index, html_element_class)
    #if html element is table
    else:
        if html_element_id != None:
            temp = soup.find(html_element, attrs={'id': html_element_id})
            if temp != None and temp:
                tables.append(temp)
        elif html_element_index != None:
            temp = soup.find_all(html_element)
            if len(temp) > html_element_index:
                tables.append(temp[html_element_index])
        else:
            temp = soup.find_all(html_element, attrs={'class': html_element_class})
            if temp != None and temp:
                tables.append(temp)
    return tables


def main():
    # collecting named arguments with ArgumentParser
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--sport')
    parser.add_argument('--html_element')
    parser.add_argument('--html_element_id')
    parser.add_argument('--html_element_index', type=int)
    parser.add_argument('--html_element_class')
    args = parser.parse_args()

    url = args.url
    sport = args.sport
    html_element = args.html_element
    html_element_id = args.html_element_id
    html_element_index = args.html_element_index
    html_element_class = args.html_element_class

    #securing right input
    n = len(sys.argv)

    if n < 3:
        print('Program take 2 arguments, --url and --sport')
        exit(-1)
    elif n > 5:
        print('Arguments id, index and class are mutually exclusive')
        exit(-1)
    elif (url == None or sport == None):
        print('Program must have arguments --url and --sport')
        exit(-1)
    elif (n > 3 and html_element == None):
        print('One of the 2 optional arguments must be --html_element')
        exit(-1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}

    session = requests.Session()
    session.headers.update(headers)
    page = session.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    tables = []

    #if optional arguments'arent null i jump in 'then' branch
    if html_element != None:
        tables = getTablesOptionalArguments(soup, html_element,html_element_id, html_element_index, html_element_class)
    else:
        tables = soup.find_all('table')

    users = []

    #collecting data from tables
    if tables:
        users = getDataFromTables(tables, sport)

    #if i did not find any users or there are no tables, i proceed to with loading iframe source
    if not users:
        body = soup.find('body')
        iframes = body.find_all('iframe')
        users = getDataFromIframes(iframes, sport, session)

    #turning array of users to Json format
    jsonString = json.dumps(users)
    print(jsonString)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
