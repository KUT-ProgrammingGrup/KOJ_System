#!/usr/bin/env python2
# coding: utf-8

import re

from datetime import timedelta

from google.appengine.ext        import db
from google.appengine.ext        import blobstore
from google.appengine.api        import users
from google.appengine.api        import urlfetch
from google.appengine.ext.webapp import template

import creole

from type import *

# 管理者かどうか返す
def is_admin():
	return users.is_current_user_admin()

# ログインしているか返す
def is_login():
	return users.get_current_user() is not None

# ページを取得
def get_page(page_id):
	query = Page.gql(u'WHERE id = :1', page_id)
	page  = query.get()
	
	return page

# 問題を取得する
def get_problem(problem_id):
	query   = Problem.gql(u'WHERE id = :1', int(problem_id))
	problem = query.get()
	
	return problem

# コンテストを取得する
def get_contest(contest_id):
	query   = Contest.gql(u'WHERE id = :1', contest_id)
	contest = query.get()
	
	return contest

# 問題の添付ファイルを取得する
def get_problem_blob(problem_id, filename):
	problem = get_problem(problem_id)
	
	for blob_key in problem.files:
		blob_info = blobstore.BlobInfo.get(blob_key)
		
		if blob_info and blob_info.filename == filename:
			return blob_info
	
	return None

# ユーザーのプロフィールを取得
def get_profile(user_id = None):
	
	if user_id is None:
		user_id = users.get_current_user().user_id
	
	query   = Profile.gql(u'WHERE id = :1', user_id)
	profile = query.get()
	
	return profile

# 解答を取得
def get_answer(problem_id, size = None, user_id = None):
	
	if size is not None and user_id is not None:
		query = Answer.gql(u'''
			WHERE problem_id = :1
				AND user_id = :2
				AND size = :3
			ORDER BY date DESC''',
				int(problem_id),
				user_id,
				size
				)
	
	else:
		query = Answer.gql(u'''
			WHERE problem_id = :1
			ORDER BY size DESC, user_id ASC, date DESC
			''',
			int(problem_id))
	
	return query

def get_nickname(user_id = None):
	
	if not user_id:
		user = users.get_current_user()
		
		if not user:
			return None
		
		user_id = user.user_id()
	
	profile = get_profile(user_id)
	
	if profile and profile.nickname:
		return profile.nickname
	
	else:
		nickname = re.sub(ur'@.+$', u'', user.nickname())
		
		profile = Profile(
				id       = user.user_id(),
				nickname = nickname
				)
		
		profile.put()
		
		return nickname


# テンプレートを読み込む
def load_template(self, path, args):
	
	# 現在のユーザーを取得
	user = users.get_current_user()
	
	# テンプレート引数を追加
	args[u'is_admin'] = users.is_current_user_admin()
	args[u'is_login'] = user is not None
	
	if user is not None:
		args[u'user_id']  = user.user_id()
		args[u'nickname'] = get_nickname()
	
	args[u'logout_url'] = users.create_logout_url(self.request.url)
	args[u'login_url']  = users.create_login_url(self.request.url)
	
	# サイドバーの読み込み
	args[u'sidebar'] = ''
	
	query = Page.gql(u'WHERE id = :1', u'sidebar')
	page  = query.get()
	
	if page:
		args[u'sidebar'] = creole2html(page.text)
	
	return template.render(path, args)

def creole2html(text):
	
	env = {
			u'is_admin': is_admin(),
			u'is_login': is_login()
			}
	
	return creole.creole2html(text, emitter_kwargs = { 'env': env })

def to_line_feed(text):
	text = text.replace(u'\r\n', u'\n')
	text = text.replace(u'\r',   u'\n')
	
	return text

# UTC -> JST
def to_jst(d):
	if d:
		return d + timedelta(hours = 9)
	
	else:
		return None

# 学内判定
def is_internal(addr):
	
	url  = u'http://www42.atpages.jp/kutpg/'
	host = [u'proxy.noc.kochi-tech.ac.jp', u'localhost']
	
	result = urlfetch.fetch(
		url,
		method           = urlfetch.GET,
		headers          = { u'X-Remote-Addr': addr },
		follow_redirects = False
		)
	
	return result.headers[u'X-Remote-Host'] in host

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
