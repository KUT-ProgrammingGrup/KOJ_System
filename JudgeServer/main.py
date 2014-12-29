#!/usr/bin/env python2.7
# coding: utf-8
# Last Change: 2011/11/15 12:52:03 +0900.

import os
import sys
import urllib
import re

# ローカル環境で use_library を使用しないとエラー
# 本環境では use_library を使用するとエラー
try:
	from google.appengine.dist import use_library
except:
	pass
else:
	use_library('django', '1.2')

from google.appengine.ext             import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from creole import creole2html

from problem import *
from page    import *
from user    import *

from contest import *

# ルートの処理
class RootHandler(webapp.RequestHandler):
	def get(self):
		
		# トップページに転送
		self.redirect('/page/index/')


def main():
	app = webapp.WSGIApplication([
		# Root
		(ur'/', RootHandler),
		
		# Page
		(ur'/page/',                         PageListHandler),
		(ur'/page/(\w+)/',                   PageHandler),
		(ur'/page/(\w+)/edit/',              PageEditHandler),
		(ur'/page/(\w+)/delete/',            PageDeleteHandler),
		(ur'/page/(\w+)/attach/',            PageAttachHandler),
		(ur'/page/(\w+)/([\w\.-]+)',         PageAttachDownloadHandler),
		(ur'/page/(\w+)/([\w\.-]+)/delete/', PageAttachDeleteHandler),
		
		# Problem
		(ur'/problem/',                                 ProblemListHandler),
		(ur'/problem/(\d+)/',                           ProblemHandler),
		(ur'/problem/(\d+)/reload/\d+/',                ProblemReloadHandler),
		(ur'/problem/(\d+)/\1-(small|large)\.(in|out)', ProblemDownloadHandler),
		(ur'/problem/(\d+)/([\w\.-]+)',                 ProblemAttachDownloadHandler),
		(ur'/problem/(\d+)/([\w\.-]+)/delete/',         ProblemAttachDeleteHandler),
		(ur'/problem/(\d+)/edit/',                      ProblemEditHandler),
		(ur'/problem/(\d+)/attach/',                    ProblemAttachHandler),
		(ur'/problem/(\d+)/submit/(small|large)/',      ProblemSubmitHandler),
		(ur'/problem/(\d+)/result/',                    ProblemResultHandler),
		(ur'/problem/(\d+)/(\d+)/(small|large)/(\d+)/', ProblemSourceDownloadHandler),
		(ur'/problem/(\d+)/delete/',                    ProblemDeleteHandler),
		
		# Contest
		(ur'/contest/',               ContestListHandler),
		(ur'/contest/(\w+)/',         ContestHandler),
		(ur'/contest/(\w+)/edit/',    ContestEditHandler),
		(ur'/contest/(\w+)/ranking/', ContestRankingHandler),
		(ur'/contest/(\w+)/delete/',  ContestDeleteHandler),
		(ur'/contest/(\w+)/(\d+)/',   ContestProblemHandler),
		
		# User
		(ur'/user/(\d+)/',      UserHandler),
		(ur'/user/(\d+)/edit/', UserEditHandler),
		
		], debug = True)

	run_wsgi_app(app)

if __name__ == '__main__':
	main()

# vim: se noet ts=4 sw=4 sts=0 ft=python :
