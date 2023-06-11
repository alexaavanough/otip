import pytest
import shutil
import sys
sys.path.append("labwork2")
sys.path.append("../")

#from labwork_2.main import *
from main import *

shutil.copy('test_for_add_book.txt', 'test_1.txt')
shutil.copy('test_for_add_book.txt', 'test_2.txt')


@pytest.mark.parametrize("author, year, name, file_path",
                         [('Author_1', '2000', 'Name_1', 'test_for_add_book.txt'),
                          ('Author_2', '1999', 'Name_2', 'test_1.txt'),
                          ('Author_3', '1998', 'Name_3', 'test_2.txt')])
def test_add_one_book(capsys, author, year, name, file_path):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"
    elk.add_book(author, year, name, file_path)
    assert elk.total_document_in_index() == 1
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  1\n"


@pytest.mark.parametrize("author, year, name, file_path",
                         [('Author_1', '2000', 'Name_1', 'notest_for_add_book.txt'),
                          ('Author_2', '1999', 'Name_2', 'notest_1.txt'),
                          ('Author_3', '1998', 'Name_3', 'notest_2.txt')])
def test_add_nonexistent_book(capsys, author, year, name, file_path):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"
    elk.add_book(author, year, name, file_path)
    captured = capsys.readouterr()
    assert captured.out == "File doesn't exist in specified directory\n"
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"


def test_add_all_books(capsys):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"
    elk.add_books("books")
    assert elk.total_document_in_index() == 6
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  6\n"


@pytest.mark.parametrize("dir_path", ["without-books", "no-books", "temp"])
def test_add_all_books(capsys, dir_path):
    elk = ElasticFunction()
    elk.create_index()
    assert elk.es.indices.exists(index=INDEX_NAME)
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"
    elk.add_books(dir_path)
    captured = capsys.readouterr()
    assert captured.out == "Directory doesn't exist in specified path\n"
    assert elk.total_document_in_index() == 0
    captured = capsys.readouterr()
    assert captured.out == "Найдено документов:  0\n"
