#!/usr/bin/env python2
# coding: utf-8

import os

from google.appengine.ext import webapp
from google.appengine.api import users

from type import *
from util import *

# ユーザーの情報を表示するハンドラ
class UserHandler(webapp.RequestHandler):
	def get(self, user_id):
		
		template_values = {
				u'user_user_id': user_id
				}
		
		# ユーザーのプロフィールが存在するか調べる
		profile = get_profile(user_id)
		
		if profile:
			if profile.nickname:
				template_values[u'user_nickname'] = profile.nickname
			
			if profile.affiliation:
				template_values[u'user_affiliation'] = profile.affiliation
			
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'user_default.html'
					)
		
		else:
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'user_none.html'
					)
		
		self.response.out.write(load_template(self, path, template_values))

# ユーザー情報を編集するハンドラ
class UserEditHandler(webapp.RequestHandler):
	
	# ユーザー情報の編集画面を表示
	def get(self, user_id):
		
		# ユーザー情報を編集する権限があるか調べる
		# 管理者 or ユーザー本人
		if not users.is_current_user_admin() and \
				users.get_current_user().user_id() != user_id:
					self.error(403)
					return
		
		# テンプレート引数を用意
		template_values = {
				u'user_user_id': user_id
				}
		
		# プロフィールを取得
		profile = get_profile(user_id)
		
		# プロフィールが存在する場合、テンプレート引数に追加
		if profile:
			if profile.nickname:
				template_values[u'user_nickname'] = profile.nickname
			
			if profile.affiliation:
				template_values[u'user_affiliation'] = profile.affiliation
		
		# テンプレートのパスを生成
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'user_edit.html'
				)
		
		# テンプレートを呼び出す
		self.response.out.write(load_template(self, path, template_values))
	
	# ユーザー情報を編集
	def post(self, user_id):
		
		# ユーザー情報を編集する権限があるか調べる
		# 管理者 or ユーザー本人
		if not users.is_current_user_admin() and \
				users.get_current_user().user_id() != user_id:
					self.error(403)
					return
		
		# プロフィールを取得
		profile = get_profile(user_id)
		
		# プロフィールが存在する場合、上書き
		if profile:
			profile.nickname    = self.request.get(u'nickname',    None)
			profile.affiliation = self.request.get(u'affiliation', None)
		
		# プロフィールが存在しない場合、新規作成
		else:
			profile = Profile(
					id          = user_id,
					nickname    = self.request.get(u'nickname',    None),
					affiliation = self.request.get(u'affiliation', None)
					)
		
		# データベースに保存
		profile.put()
		
		self.redirect(u'/user/{0}/'.format(user_id))

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
