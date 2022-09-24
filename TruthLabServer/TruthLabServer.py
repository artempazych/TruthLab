from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify
import os
import jinja2
import TruthLabDatabase
import pymorphy2
import nltk
import re
import string
import glob
import json
from codecs import open
from tokenize_uk import tokenize_text, tokenize_words, tokenize_sents
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import html2text
import csv
import cgi
import pymysql
try:
    import http.server as server
except ImportError:
    import SimpleHTTPServer as server
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.cluster import KMeans
import json
import os.path

nltk.download()
database = TruthLabDatabase.TruthLabDatabase('localhost', 'truthlab_main', 'truthlab', 'truthlab_fake-news')

app = Flask(__name__)
app.secret_key = 'TruthLab2020'

# Задаємо шлях до директорії з шаблонами HTML-сторінок
template_dir = os.getcwd()+'/templates'
loader = jinja2.FileSystemLoader(template_dir)
environment = jinja2.Environment(loader=loader)

class TruthLabTokenizer:
    def __init__(self, language):
        self.language = language
        self.morph = pymorphy2.MorphAnalyzer(lang=language)

    def tokenize(self, text):
        # видалення чисел
        text = re.sub(r'\d+', '', text)
        # виокремлення лексем (токенів)
        lexems = nltk.word_tokenize(text)
        # видалення знаків пунктуації
        punctuationRegex = re.compile(r'\w+')
        lexems = list(filter(punctuationRegex.match, lexems))
        # приведення слів до нормальної форми
        normal_lexems = []
        for word in lexems:
            word = self.morph.parse(word)[0].normal_form
            normal_lexems.append(word)
        lexems = normal_lexems
        # видалення стоп-слів української мови
        stop_words = []
        if self.language == 'uk':
            stop_words = [line.rstrip('\n') for line in open("data/ukrainian-stopwords.txt", encoding = "ISO-8859-1")]
        filtered_lexems = [w for w in lexems if not w in stop_words]
        lexems = filtered_lexems

        return lexems

class TruthLabWebScraper:
    def __init__(self):
        return

    def scrape_links(self, url, items_selector, links_selector):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        link_lists = []
        for article in soup.select(items_selector):
            for a in article.select(links_selector):
                link_lists.append(a['href'])
        return link_lists

    def scrape_texts(self, list_urls, text_selector):
        text_lists = []
        for url in list_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            text = str(soup.select(text_selector))
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            text = h.handle(text)
            text_lists.append([text, url])
        return text_lists

    def save_array_to_csv(self, file_name, arr):
        wtr = csv.writer(open(file_name, 'w', 'utf-8'), delimiter=',', lineterminator='\n')
        for x in arr:
            wtr.writerow(x)

    def load_array_from_csv(self, file_name):
        rdr = csv.reader(open(file_name, 'r', 'utf-8'), delimiter=',', lineterminator='\n')
        arr = []
        for x in rdr:
            if len(x[0]) > 0:
                arr.append(x)
        return arr

class TruthLabAlgorithms:
    def __init__(self):
        self.themesFit()
        self.languagesFit()
        self.spamFit()
        self.fakeFit()

    def themesFit(self):
        self.text_clf_themes = Pipeline([
            ('countvect', CountVectorizer()),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ('clf', SGDClassifier(loss='hinge')),
        ])
        rows = database.getThemes()
        data = {'x' : [], 'y' : []}
        for elem in rows:
            data['x'].append(elem['text'])
            data['y'].append(elem['name'])
        self.text_clf_themes.fit(data['x'], data['y'])

    def themePredict(self, text):
        tokenizer = TruthLabTokenizer('uk')
        tokenizedText = tokenizer.tokenize(text)
        return self.text_clf_themes.predict([' '.join(tokenizedText)])

    def languagesFit(self):
        self.text_clf_languages = Pipeline([
            ('countvect', CountVectorizer()),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ('clf', SGDClassifier(loss='hinge')),
        ])
        rows = database.getLanguages()
        data = {'x' : [], 'y' : []}
        for elem in rows:
            data['x'].append(elem['text'])
            data['y'].append(elem['name'])
        self.text_clf_languages.fit(data['x'], data['y'])

    def languagePredict(self, text):
        tokenizer = TruthLabTokenizer('uk')
        tokenizedText = tokenizer.tokenize(text)
        return self.text_clf_languages.predict([' '.join(tokenizedText)])

    def spamFit(self):
        self.text_clf_spam = Pipeline([
            ('countvect', CountVectorizer()),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ('clf', SGDClassifier(loss='hinge')),
        ])
        rows = database.getSpamAndNoSpam()
        data = {'x' : [], 'y' : []}
        for elem in rows:
            data['x'].append(elem['text'])
            data['y'].append(elem['name'])
        self.text_clf_spam.fit(data['x'], data['y'])

    def spamPredict(self, text):
        tokenizer = TruthLabTokenizer('uk')
        tokenizedText = tokenizer.tokenize(text)
        return self.text_clf_spam.predict([' '.join(tokenizedText)])

    def fakeFit(self):
        self.text_clf_fake = Pipeline([
            ('countvect', CountVectorizer()),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ('clf', SGDClassifier(loss='hinge')),
        ])
        rows = database.getFakeAndNoFakes()
        data = {'x' : [], 'y' : []}
        for elem in rows:
            data['x'].append(elem['text'])
            data['y'].append(elem['name'])
        self.text_clf_fake.fit(data['x'], data['y'])

    def fakePredict(self, text):
        tokenizer = TruthLabTokenizer('uk')
        tokenizedText = tokenizer.tokenize(text)
        return self.text_clf_fake.predict([' '.join(tokenizedText)])

    def complexPredict(self, text):
        tokenizer = TruthLabTokenizer('uk')
        tokenizedText = tokenizer.tokenize(text)
        predicat = [' '.join(tokenizedText)]
        labelLanguage = self.text_clf_languages.predict(predicat)
        labelTheme = self.text_clf_themes.predict(predicat)
        labelSpam = self.text_clf_spam.predict(predicat)
        labelFake = self.text_clf_fake.predict(predicat)
        return {'text' : text, 'language' : labelLanguage[0], 'theme' : labelTheme[0], 'spam' : labelSpam[0], 'fake' : labelFake[0]}

algorithm = TruthLabAlgorithms()


# -- Обробник звернення до головної сторінки --
@app.route('/')
def index():
    # якщо користувач аутентифікований, то відображаємо йому головну сторінку
    # if 'login' in session:
    #print(session)
    #return render_template('index.html', session=session, page='first-page.html', themes=database.getThemes(), languages=database.getLanguages(), spam=database.getSpam(), fake=database.getFake(), profile={'login' : session['login'], 'username' : session['username']})
    return render_template('index.html', session=session, page='first-page.html')
    #else:
        # якщо користувач не аутентифікований, то переадресувати його на сторінку аутентифікації
    #    return redirect(url_for('user_login'))
    #

@app.route('/user')
def index_user():
    # якщо користувач аутентифікований, то відображаємо йому головну сторінку
    if 'login' in session:
    #print(session)
        return render_template('index.html', session=session, page='main.html', themes=database.getThemes(), languages=database.getLanguages(), spam=database.getSpam(), fake=database.getFake(), profile={'login' : session['login'], 'username' : session['username']})
    else:
        # якщо користувач не аутентифікований, то переадресувати його на сторінку аутентифікації
        return redirect(url_for('/'))

# -- Обробники модуля "Користувачі сайту" --


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if 'login' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = database.getUserByLoginAndPassword(login, password)
        if (user != None):
            session['login'] = user['login']
            session['access'] = user['access']
            session['username'] = user['username']
            return redirect(url_for('index_user'))
        else:
            return render_template('index.html', page='user/login.html', error='Неправильний логін або пароль')
    return render_template('index.html', page='user/login.html')


@app.route('/user/logout')
def user_logout():
    session.pop('login', None)
    session.pop('access', None)
    return redirect(url_for('index'))


@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if 'login' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        result = database.addUser(request.form['login'], request.form['password1'], request.form['password2'], request.form['username'], 'full')
        if result == True:
            session['login'] = request.form['login']
            session['access'] = 'full'
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return render_template('index.html', page='user/register.html', error=result)
    return render_template('index.html', page='user/register.html')\


@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile_get():
    if 'login' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('user/profile.html', profile={'login' : session['login'], 'username' : session['username']})
    if request.method == 'POST':
        user = database.getUserByLogin(session['login'])
        database.editUser(user['id'], request.form['password1'], request.form['password2'], request.form['username'])
        user = database.getUserByLogin(session['login'])
        session['username'] = user['username']
        return render_template('user/profile.html', profile={'login': session['login'], 'username': session['username']})

# Themes

@app.route('/theme/add', methods=['POST'])
def theme_add():
    if 'login' not in session:
        return redirect(url_for('index'))
    name = request.form['name']
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.themeAdd(name, ' '.join(tokenizedText))
    return jsonify(status="OK")


@app.route('/theme/predict', methods=['POST'])
def theme_predict():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    return jsonify(label=algorithm.themePredict(text)[0])

@app.route('/theme/getlist', methods=['GET', 'POST'])
def theme_getlist():
    if 'login' not in session:
        return redirect(url_for('index'))
    return render_template('themes/list.html', themes=database.getThemes())

@app.route('/theme/delete/<id>', methods=['GET', 'POST'])
def theme_delete(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    database.deleteTheme(id)
    return jsonify(status="OK")

@app.route('/theme/edit/<id>', methods=['GET'])
def theme_edit(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    theme = database.getTheme(id)
    if theme != None:
        return render_template('themes/edit.html', theme=theme)
    else:
        return ''

@app.route('/theme/edit/<id>', methods=['POST'])
def theme_edit_post(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    name = request.form['name']
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.editTheme(id, name, ' '.join(tokenizedText))
    return jsonify(status="OK")

# Languages

@app.route('/language/add', methods=['POST'])
def language_add():
    if 'login' not in session:
        return redirect(url_for('index'))
    name = request.form['name']
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.languageAdd(name, ' '.join(tokenizedText))
    return jsonify(status="OK")


@app.route('/language/predict', methods=['POST'])
def language_predict():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    return jsonify(label=algorithm.languagePredict(text)[0])

@app.route('/language/getlist', methods=['GET', 'POST'])
def language_getlist():
    if 'login' not in session:
        return redirect(url_for('index'))
    return render_template('languages/list.html', languages=database.getLanguages())

@app.route('/language/delete/<id>', methods=['GET', 'POST'])
def language_delete(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    database.deleteLanguage(id)
    return jsonify(status="OK")

@app.route('/language/edit/<id>', methods=['GET'])
def language_edit(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    language = database.getLanguage(id)
    if language != None:
        return render_template('languages/edit.html', language=language)
    else:
        return ''

@app.route('/language/edit/<id>', methods=['POST'])
def language_edit_post(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    name = request.form['name']
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.editLanguage(id, name, ' '.join(tokenizedText))
    return jsonify(status="OK")

# Spam

@app.route('/spam/add', methods=['POST'])
def spam_add():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.spamAdd(' '.join(tokenizedText))
    return jsonify(status="OK")


@app.route('/spam/predict', methods=['POST'])
def spam_predict():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    return jsonify(label=algorithm.spamPredict(text)[0])

@app.route('/spam/getlist', methods=['GET', 'POST'])
def spam_getlist():
    if 'login' not in session:
        return redirect(url_for('index'))
    return render_template('spam/list.html', spam=database.getSpam())

@app.route('/spam/delete/<id>', methods=['GET', 'POST'])
def spam_delete(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    database.deleteSpam(id)
    return jsonify(status="OK")

@app.route('/spam/edit/<id>', methods=['GET'])
def spam_edit(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    spam = database.getSpam(id)
    if spam != None:
        return render_template('spam/edit.html', spam=spam)
    else:
        return ''

@app.route('/spam/edit/<id>', methods=['POST'])
def spam_edit_post(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.editSpam(id, ' '.join(tokenizedText))
    return jsonify(status="OK")

# Fake

@app.route('/fake/add', methods=['POST'])
def fake_add():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.fakeAdd(' '.join(tokenizedText))
    return jsonify(status="OK")


@app.route('/fake/predict', methods=['POST'])
def fake_predict():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    return jsonify(label=algorithm.fakePredict(text)[0])

@app.route('/fake/getlist', methods=['GET', 'POST'])
def fake_getlist():
    if 'login' not in session:
        return redirect(url_for('index'))
    return render_template('fake/list.html', fake=database.getFake())

@app.route('/fake/delete/<id>', methods=['GET', 'POST'])
def fake_delete(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    database.deleteFake(id)
    return jsonify(status="OK")

@app.route('/fake/edit/<id>', methods=['GET'])
def fake_edit(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    fake = database.getFake(id)
    if fake != None:
        return render_template('fake/edit.html', fake=fake)
    else:
        return ''

@app.route('/fake/edit/<id>', methods=['POST'])
def fake_edit_post(id):
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    tokenizer = TruthLabTokenizer('uk')
    tokenizedText = tokenizer.tokenize(text)
    database.editFake(id, ' '.join(tokenizedText))
    return jsonify(status="OK")

# Complex Analisis
@app.route('/complex/predict', methods=['POST'])
def complex_predict():
    if 'login' not in session:
        return redirect(url_for('index'))
    text = request.form['text']
    return render_template('complex/list.html', result=algorithm.complexPredict(text))

# Administrate
@app.route('/admin/themefit', methods=['GET'])
def admin_themefit():
    if 'login' not in session:
        return redirect(url_for('index'))
    if session['access'] != 'admin':
        return redirect(url_for('index'))
    algorithm.themesFit()
    return jsonify(status="Перенавчання алгоритму модуля 'Теми' виконано успішно")

@app.route('/admin/languagefit', methods=['GET'])
def admin_languagefit():
    if 'login' not in session:
        return redirect(url_for('index'))
    if session['access'] != 'admin':
        return redirect(url_for('index'))
    algorithm.languagesFit()
    return jsonify(status="Перенавчання алгоритму модуля 'Мови' виконано успішно")

@app.route('/admin/spamfit', methods=['GET'])
def admin_spamfit():
    if 'login' not in session:
        return redirect(url_for('index'))
    if session['access'] != 'admin':
        return redirect(url_for('index'))
    algorithm.spamFit()
    return jsonify(status="Перенавчання алгоритму модуля 'Спам' виконано успішно")

@app.route('/admin/fakefit', methods=['GET'])
def admin_fakefit():
    if 'login' not in session:
        return redirect(url_for('index'))
    if session['access'] != 'admin':
        return redirect(url_for('index'))
    algorithm.fakeFit()
    return jsonify(status="Перенавчання алгоритму модуля 'Фейки' виконано успішно")

@app.route('/user/list', methods=['GET'])
def user_list():
    if 'login' not in session:
        return ''
    if session['access'] != 'admin':
        return ''
    return render_template('user/list.html', users=database.getUsers())\

@app.route('/user/delete/<id>', methods=['GET', 'POST'])
def user_delete(id):
    if 'login' not in session:
        return ''
    if session['access'] != 'admin':
        return ''
    database.deleteUser(id)
    return jsonify(status="OK")

@app.route('/user/edit/<id>', methods=['GET'])
def user_edit(id):
    if 'login' not in session:
        return ''
    if session['access'] != 'admin':
        return ''
    user = database.getUserById(id)
    if user != None:
        return render_template('user/edit.html', user=user)
    else:
        return ''

@app.route('/user/edit/<id>', methods=['POST'])
def uesr_edit_post(id):
    if 'login' not in session:
        return ''
    if session['access'] != 'admin':
        return ''
    database.editUserByAdmin(id, request.form['password'], request.form['username'], request.form['access'])
    return jsonify(status="OK")

if __name__ == '__main__':
    app.run('truthlab.com.ua', 8000)