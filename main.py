import psycopg

from bs4 import BeautifulSoup

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage

class Page(QWebEnginePage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))
        self.app.exec_()

    def _on_load_finished(self):
        self.html = self.toHtml(self.Callable)
        print('Load finished')

    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()

cridentials = open(".env", "r").read().splitlines()

with psycopg.connect(
  host=cridentials[0],
  port=cridentials[1],
  user=cridentials[2],
  password=cridentials[3]
) as conn:
  with conn.cursor() as cur:
    cur.execute("""
      SELECT (id, "Twitter", "Reddit")
      FROM authors
      WHERE "isReviewer" = true
    """)
    for i in cur.fetchall():
      page = Page(i[0][1][1:-1])
      print(page.html)
      soup = BeautifulSoup(page.html, 'html.parser')

      followElement = soup.select('div.r-13awgt0:nth-child(5) > div:nth-child(2) > a:nth-child(1) > span:nth-child(1) > span:nth-child(1)')

      print(followElement)