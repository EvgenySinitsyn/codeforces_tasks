from task import Task
from bs4 import BeautifulSoup
import requests


def number_of_pages_count(url, headers):
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser")
    number = int(soup.find('div', class_='pagination').findAll('span')[-1].text.strip())
    return number


def parce_page(url, headers, cursor, existing_tasks):
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser")
    tr = soup.find('table').findAll('tr')

    for line in tr[1:]:
        task = Task()
        table_line = line.findAll("td")
        task.number = table_line[0].text.strip()
        name_categories_tags = table_line[1].findAll('div')
        task.title = name_categories_tags[0].text.strip()
        task.categories = [category.text.strip() for category in name_categories_tags[1].findAll('a')]
        task.difficulty = table_line[3].text.strip()
        task.link = table_line[0].find('a')['href']
        solved_quantoty = table_line[-1].text.strip()[1:]
        task.solved_quantity = int(solved_quantoty) if solved_quantoty else 0
        task.add_to_DB(cursor, existing_tasks)
