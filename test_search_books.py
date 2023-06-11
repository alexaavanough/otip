import pytest
import sys
sys.path.append("labwork2")
sys.path.append("../")

#from labwork_2.main import *
from main import *


@pytest.mark.parametrize("word, print_result, value_result",
                         [("день", 'Найдено: 3\nЕсть в осени первоначальной - Тютчев - 1851'
                                   '\nТуча - Пушкин - 1835\nЗимнее утро - Пушкин - 1829\n',
                           [('Есть в осени первоначальной', 'Тютчев', '1851'),
                            ('Туча', 'Пушкин', '1835'), ('Зимнее утро', 'Пушкин', '1829')]),
                          ("красавица", "Найдено: 1\nЗимнее утро - Пушкин - 1829\n", [('Зимнее утро', 'Пушкин', '1829')]),
                          ("ночь", "Найдено: 0\n", None)])
def test_search_books_with_words(capsys, word, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    assert elk.search_books_with_words(word) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("word, print_result, value_result",
                         [("день", "Найдено: 0\n", None),
                          ("красавица", "Найдено: 0\n", None),
                          ("ночь", "Найдено: 0\n", None)])
def test_search_books_with_words_without_document(capsys, word, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert elk.search_books_with_words(word) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("word, author, print_result, value_result", [('день', 'Пушкин', 'Найдено: 2\n'
                                                                                         'Туча - Пушкин - 1835\nЗимнее утро - Пушкин - 1829\n',
                                                                       [('Туча', 'Пушкин', '1835'), ('Зимнее утро', 'Пушкин', '1829')]),
                                                                      ('красавица', 'Пушкин',
                                                                       "Найдено: 1\nЗимнее утро - Пушкин - 1829\n",
                                                                       [('Зимнее утро', 'Пушкин', '1829')]),
                                                                      ('ночь', 'Тютчев', 'Найдено: 0\n', None),
                                                                      ('абракадабра', 'Неавтор', 'Найдено: 0\n', None),
                                                                      ('дубовый', 'Лермонтов',
                                                                       'Найдено: 1\nЛисток - Лермонтов - 1841\n',
                                                                       [('Листок', 'Лермонтов', '1841')])])
def test_search_books(capsys, word, author, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    assert elk.search_books(author, word) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("word, author, print_result, value_result", [('день', 'Пушкин', 'Найдено: 0\n', None),
                                                                      ('ночь', 'Тютчев', 'Найдено: 0\n', None),
                                                                      ('абракадабра', 'Неавтор', 'Найдено: 0\n', None),
                                                                      ('дубовый', 'Лермонтов', 'Найдено: 0\n', None)])
def test_search_books_without_document(capsys, word, author, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert elk.search_books(author, word) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("first_date, till_date, word, result",
                         [('1825', '1830', 'лес', 'Найдено: 1\nВесенняя гроза - Тютчев - 1828\n'),
                          ('1835', '1835', 'парус', 'Найдено: 1\nТуча - Пушкин - 1835\n'),
                          ('1950', '1965', 'парус', 'Найдено: 0\n'),
                          ('1800', '1900', 'абракадабра',
                           'Найдено: 6\nЕсть в осени первоначальной - Тютчев - 1851\nЛисток - Лермонтов - 1841\n'
                           'Туча - Пушкин - 1835\nПарус - Лермонтов - 1835\n'
                           'Зимнее утро - Пушкин - 1829\nВесенняя гроза - Тютчев - 1828\n')])
def test_search_in_interval_date_print_value(capsys, first_date, till_date, word, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    elk.search_in_interval_dates(first_date, till_date, word)
    captured = capsys.readouterr()
    assert captured.out == result


@pytest.mark.parametrize("first_date, till_date, word, result",
                         [('1825', '1830', 'лес', [('Весенняя гроза', 'Тютчев', '1828')]),
                          ('1835', '1835', 'парус', [('Туча', 'Пушкин', '1835')]),
                          ('1950', '1965', 'парус', None),
                          ('1800', '1900', 'абракадабра',
                           [('Есть в осени первоначальной', 'Тютчев', '1851'),('Листок', 'Лермонтов', '1841'),
                            ('Туча', 'Пушкин', '1835'),('Парус', 'Лермонтов', '1835'),
                            ('Зимнее утро', 'Пушкин', '1829'),('Весенняя гроза', 'Тютчев', '1828')])])
def test_search_in_interval_date_return_value(capsys, first_date, till_date, word, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    assert elk.search_in_interval_dates(first_date, till_date, word) == result


@pytest.mark.parametrize("first_date, till_date, word, result",
                         [('1825', '1830', 'лес', 'Найдено: 0\n'),
                          ('1835', '1835', 'парус', 'Найдено: 0\n'),
                          ('1950', '1965', 'парус', 'Найдено: 0\n'),
                          ('1800', '1900', 'абракадабра', 'Найдено: 0\n')])
def test_search_in_interval_date_without_document(capsys, first_date, till_date, word, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.search_in_interval_dates(first_date, till_date, word)
    captured = capsys.readouterr()
    assert captured.out == result


@pytest.mark.parametrize("first_date, till_date, word, result",
                         [('1825', '1830', 'лес', None),
                          ('1835', '1835', 'парус', None),
                          ('1950', '1965', 'парус', None),
                          ('1800', '1900', 'абракадабра', None)])
def test_search_in_interval_date_without_document_return_value(capsys, first_date, till_date, word, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    assert elk.search_in_interval_dates(first_date, till_date, word) == result
