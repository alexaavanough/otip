import pytest
import sys
sys.path.append("labwork2")
sys.path.append("../")

#from labwork_2.main import *
from main import *


@pytest.mark.parametrize("author, print_result, value_result", [('Пушкин', 'Среднее арифметическое для годов издания - 1832\n', 1832),
                                            ('Лермонтов', 'Среднее арифметическое для годов издания - 1838\n', 1838),
                                            ('Тютчев', 'Среднее арифметическое для годов издания - 1840\n', 1840)])
def test_calculate_average_dates(capsys, author, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    assert elk.calculate_average_date(author) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("author, print_result, value_result", [('Пушкин', 'Не найдены книги заданного автора\n', None),
                                            ('Лермонтов', 'Не найдены книги заданного автора\n', None),
                                            ('Тютчев', 'Не найдены книги заданного автора\n', None)])
def test_calculate_average_dates_without_document(capsys, author, print_result, value_result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert elk.calculate_average_date(author) == value_result
    captured = capsys.readouterr()
    assert captured.out == print_result


@pytest.mark.parametrize("year, result", [('1835', 'одна   3\nсчастия   2\nлазури   2\nищет   '
                                                   '2\nветер   2\nбури   2\nясной   '
                                                   '1\nуспокоенных   1\nунылую   1\nувы   1\n'),
                                          ('1829', 'солнце   2\nсквозь   2\nмилый   2\nдруг   '
                                                   '2\nянтарным   1\nявись   1\nчудесный   '
                                                   '1\nчернеет   1\nутреннему   1\nтучи   1\n'),
                                          ('1900', 'Не найдено книг в указанный год\n')])
def test_top_words(capsys, year, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    elk.top_words(year)
    captured = capsys.readouterr()
    assert captured.out == result


@pytest.mark.parametrize("year, result", [('1835', 'Не найдено книг в указанный год\n'),
                                          ('1829', 'Не найдено книг в указанный год\n'),
                                          ('1900', 'Не найдено книг в указанный год\n')])
def test_top_words_without_document(capsys, year, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    elk.top_words(year)
    captured = capsys.readouterr()
    assert captured.out == result


@pytest.mark.parametrize("year, result", [('1835', [('одна', 3), ('счастия', 2), ('лазури', 2), ('ищет', 2), ('ветер', 2),
                                                    ('бури', 2), ('ясной', 1), ('успокоенных', 1), ('унылую', 1), ('увы', 1)]),
                                          ('1829', [('солнце', 2), ('сквозь', 2), ('милый', 2), ('друг', 2), ('янтарным', 1),
                                                    ('явись', 1), ('чудесный', 1), ('чернеет', 1), ('утреннему', 1), ('тучи', 1)]),
                                          ('1900', 0)])
def test_top_words_return_value(capsys, year, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    assert elk.top_words(year) == result


@pytest.mark.parametrize("year, result", [('1835', 0),
                                          ('1829', 0),
                                          ('1900', 0)])
def test_top_words_without_document_return_value(capsys, year, result):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    assert elk.top_words(year) == result