#!/usr/bin/env python27
# coding: utf-8
# Last Change: 2011/11/06 20:29:08 +0900.

from google.appengine.ext import db
from google.appengine.ext import blobstore

# ページのデータ
class Page(db.Model):
	id       = db.StringProperty(required = True)
	title    = db.StringProperty(required = True)
	text     = db.TextProperty(required = True)	
	files    = db.ListProperty(blobstore.BlobKey)
	date     = db.DateTimeProperty(auto_now = True)
	public   = db.BooleanProperty(required = True, default = True) # 公開するかどうか
	internal = db.BooleanProperty(required = True, default = False)

# 問題のデータ
class Problem(db.Model):
	id           = db.IntegerProperty(required = True) # 問題ID
	title        = db.StringProperty(required = True)
	text         = db.TextProperty(default = u'<<nop />>')
	public       = db.BooleanProperty(required = True, default = False) # 問題を公開するかどうか
	files        = db.ListProperty(blobstore.BlobKey) # 添付ファイル
	input_small  = db.TextProperty()
	input_large  = db.TextProperty()
	output_small = db.TextProperty()
	output_large = db.TextProperty()
	date         = db.DateTimeProperty(auto_now = True)

# 解答のデータ
class Answer(db.Model):
	user_id    = db.StringProperty(required = True)
	problem_id = db.IntegerProperty(required = True)
	size       = db.StringProperty(required = True)
	source     = db.BlobProperty(required = True)
	filename   = db.TextProperty(required = True)
	date       = db.DateTimeProperty(auto_now = True)

# コンテストのデータ
class Contest(db.Model):
	id          = db.StringProperty(required = True) # コンテスト ID
	title       = db.StringProperty(required = True) # コンテストタイトル
	page        = db.StringProperty() # コンテストの詳細ページ
	start_date  = db.DateTimeProperty() # 開始日時
	end_date    = db.DateTimeProperty() # 終了日時
	problem     = db.ListProperty(int, required = True) # 問題の一覧
	point_small = db.ListProperty(int, required = True) # small の点数
	point_large = db.ListProperty(int, required = True) # large の点数
	public      = db.BooleanProperty(required = True)

# ユーザーのプロフィールデータ
class Profile(db.Model):
	id          = db.StringProperty(required = True)
	nickname    = db.StringProperty()
	affiliation = db.TextProperty()

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
