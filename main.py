"""
    Laboratory Work #2
"""

import os
import re
from statistics import mean

from elasticsearch_dsl import (Document,
                               connections,
                               analysis,
                               Text,
                               Keyword,
                               analyzer,
                               tokenizer,
                               Search)
import click

INDEX_NAME = '2018-3-08-dav'


# https://elasticsearch-dsl.readthedocs.io/en/latest/

class Article(Document):
    """
        Mapping
    """
    my_token_filter = analysis.token_filter('my_token_filter',
                                            type='stop',
                                            stopwords=["_russian_", "князь", "повезет", "сорок"])

    my_analyzer = analyzer('my_analyzer',
                           tokenizer=tokenizer('standard'),
                           filter=['lowercase', my_token_filter])

    title = Keyword()
    author = Keyword()
    year = Keyword()
    content = Text(analyzer=my_analyzer)

    class Index:
        """
            Definition of name and setting
        """
        name = INDEX_NAME
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 2,
        }


class ElasticFunction:

    def __init__(self):

        host = 'localhost'
        port = 9200
        self.es = connections.create_connection(host=host, port=port)
        # ES = connections.create_connection(hosts=['localhost'])

    def add_book(self, author, year, title, file_path):
        """
            Method that implements adding a new document to the index by parameters,
            regardless of the file name
        """

        if not (os.path.exists(file_path) or os.path.isfile(file_path)):
            print("File doesn't exist in specified directory")
            return

        with open(file_path, 'r', encoding="UTF-8") as file:
            text = file.read()
            article = Article()
            article.title = str(title)
            article.content = str(text)
            article.year = str(year)
            article.author = str(author)
            article.save()
            self.es.indices.refresh(index=INDEX_NAME)

    def create_index(self):
        """
            Create the mappings in elasticsearch
        """
        if self.es.indices.exists(index=INDEX_NAME):
            self.es.indices.delete(index=INDEX_NAME)
        Article.init()

    def add_books(self, dir_path):
        """
            A method that implements the addition of all documents in a given directory
            named after a pattern "название - автор - год издания"
        """
        all_files = []
        if not (os.path.exists(dir_path) and os.path.isdir(dir_path)):
            print("Directory doesn't exist in specified path")
            return

        for i in os.walk(dir_path):
            all_files.append(i)

        for path, _, files in all_files:
            for file in files:
                # название - автор - год издания. txt
                file_name = file.replace(".txt", "")
                # название - автор - год издания
                if re.search(r'.+\-.+\-.*\d{4}.*', file_name):
                    file_split = file_name.split("-")
                    # --> ['название','автор','год']
                    title = file_split[0].strip()
                    author = file_split[1].strip()
                    year = file_split[2].strip()
                    file_path = path + '/' + file

                    self.add_book(author, year, title, file_path)

    def search_books_with_words(self, word):
        """
            A method that implements the search for all books with a given word.
            Displays the number of books with this word, and below -
            a list of these books with authors and year of publication.
        """
        s = Search(using=self.es, index=INDEX_NAME).query("match", content=word)
        response = s.execute()
        print("Найдено:", response.hits.total.value)
        if response.hits.total.value == 0:
            return
        books_list = list(response)
        books_list.sort(key=lambda x: x.year, reverse=True)
        result_list = []
        for book in books_list:
            result_list.append((book.title, book.author, book.year))
            print(book.title + ' - ' + book.author + ' - ' + book.year)
        return result_list

    def total_document_in_index(self):
        """
            Additional method that determines the total number of documents in the index
        """
        quantity = self.es.count(index=INDEX_NAME)['count']
        print("Найдено документов: ", quantity)
        return quantity

    def search_books(self, author, word):
        """
            A method that searches for all books by a given author that contain a given string.
            Displays the number of books by the author with this word,
            and below - a list of these books with the author and year of publication.
        """
        s = Search(using=self.es, index=INDEX_NAME) \
            .query("match", content=word) \
            .query("match", author=author)
        response = s.execute()
        print("Найдено:", response.hits.total.value)
        if response.hits.total.value == 0:
            return
        books_list = list(response)
        books_list.sort(key=lambda x: x.year, reverse=True)
        result_list = []
        for book in books_list:
            result_list.append((book.title, book.author, book.year))
            print(book.title + ' - ' + book.author + ' - ' + book.year)
        return result_list

    def search_in_interval_dates(self, from_date, till_date, word):
        """
            A method that searches for all books in the specified range of years
            that do not contain the specified string.
            Displays the number of books with this word, and below -
            a list of these books with authors and year of publication.
        """
        s = Search(using=self.es, index=INDEX_NAME) \
            .query('range',
                   **{"year": {"gte": from_date, "lte": till_date}}) \
            .exclude("match", content=word)
        response = s.execute()
        print("Найдено:", response.hits.total.value)
        if response.hits.total.value == 0:
            return
        books_list = list(response)
        books_list.sort(key=lambda x: (x.year, x.author), reverse=True)
        result_list = []
        for book in books_list:
            result_list.append((book.title, book.author, book.year))
            print(book.title + ' - ' + book.author + ' - ' + book.year)
        return result_list

    def calculate_average_date(self, author):
        """
            A method that calculates the arithmetic mean for the year of publication of a given author.
            Displays the average of the rounded average
        """
        dates = []
        s = Search(using=self.es, index=INDEX_NAME).query("match", author=author)
        response = s.execute()
        for hit in response:
            dates.append(int(hit.year))

        if len(dates) == 0:
            print('Не найдены книги заданного автора')
            return
        else:
            average_date = (round(mean(dates)))
            print('Среднее арифметическое для годов издания - ' + str(average_date))
            return average_date

    def top_words(self, year):
        """
            A method that implements the definition of the top 10 most popular
            words with the number of their mentions in all books
            of the given year contained in the index.
        """
        top_n = 10
        terms = {}
        s = Search(using=self.es, index=INDEX_NAME).query("match", year=year)
        response = s.execute()
        if response.hits.total.value == 0:
            print("Не найдено книг в указанный год")
            return 0

        for book in response:
            tvs = self.es.termvectors(id=book.meta.id, index=INDEX_NAME, fields=['content'])
            for term, freq in tvs['term_vectors']['content']['terms'].items():
                if term in terms:
                    terms[term] += freq['term_freq']
                else:
                    terms[term] = freq['term_freq']

        terms_list = list(terms.items())

        terms_list.sort(key=lambda x: (x[1], x[0]), reverse=True)
        for term in terms_list[:top_n]:
            print(term[0], ' ', term[1])
        return terms_list[:top_n]


@click.group()
def main():
    """main group function for click module"""


@main.command(name='create-index', help='Create the mappings in elasticsearch')
def create_st():
    """function for click module"""
    elk.create_index()


@main.command(name='total-document', help='Display count of document in index')
def total_document_st():
    """function for click module"""
    elk.total_document_in_index()


@main.command(name='add-book', help='Method that implements adding a new document '
                                    'to the index by parameters, regardless of the file name')
@click.option('-a', '--author', required=True)
@click.option('-y', '--year', required=True)
@click.option('-n', '--name', required=True)
@click.option('-p', '--path', required=True)
def add_book_st(author, year, name, path):
    """function for click module"""
    elk.add_book(author, year, name, path)


@main.command(name='add-books', help=' A method that implements the addition of all '
                                     'documents in a given directory named after'
                                     ' a pattern "название - автор - год издания"')
@click.argument('path')
def add_books_st(path):
    """function for click module"""
    elk.add_books(path)


@main.command(name='books-with-words',
              help='A method that implements the search for all books with a given word.'
                   ' Displays the number of books with this word, and below -'
                   'a list of these books with authors and year of publication.')
@click.argument('word')
def search_books_with_words_st(word):
    """function for click module"""
    elk.search_books_with_words(word)


@main.command(name='search-books',
              help='A method that searches for all books by a given author'
                   'that contain a given string.'
                   'Displays the number of books by the author with this word, and below -'
                   'a list of these books with the author and year of publication.')
@click.option('-a', '--author', required=True)
@click.argument('word')
def search_books_st(author, word):
    """function for click module"""
    elk.search_books(author, word)


@main.command(name='search-in-dates',
              help='A method that searches for all books in the specified range of years'
                   'that do not contain the specified string.'
                   'Displays the number of books with this word, and below - '
                   'a list of these books with authors and year of publication.')
@click.option('-f', '--first_date', type=int, required=True)
@click.option('-t', '--till', type=int, required=True)
@click.argument('word')
def search_dates_st(first_date, till, word):
    """function for click module"""
    elk.search_in_interval_dates(first_date, till, word)


@main.command(name='calc-date',
              help='A method that calculates the arithmetic mean for the'
                   'year of publication of a given author.'
                   'Displays the average of the rounded average')
@click.option('-a', '--author', required=True)
def calculate_average_date_st(author):
    """function for click module"""
    elk.calculate_average_date(author)


@main.command(name='top-words', help='A method that implements the definition of the'
                                     'top 10 most popular'
                                     'words with the number of their mentions in all books'
                                     'of the given year contained in the index.')
@click.option('-d', '--date', type=int, required=True)
def top_words_st(date):
    """function for click module"""
    elk.top_words(date)


@main.command(name='run-tests', help='PyTests for main function. Coverage 60%')
def run_test(self):
    """function for click module"""
    os.system('python3 -m pytest --cov=main tests/')


if __name__ == '__main__':
    elk = ElasticFunction()
    main()
