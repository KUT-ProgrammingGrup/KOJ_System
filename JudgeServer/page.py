#!/usr/bin/env python2.7
# coding: utf-8

# page.py
# ページ ハンドラ

# Last Change: 2011/11/14 16:57:25 +0900.

import os
import urllib

from google.appengine.ext        import webapp
from google.appengine.ext.webapp import blobstore_handlers

from type import *
from util import *

import util

# ページのベースハンドラ
class PageBaseHandler(webapp.RequestHandler):
	def get_page(self, page_id):
		query = Page.gql(u'WHERE id = :1', page_id)
		page  = query.get()
		
		return page
	
	def get_blob(self, page_id, filename):
		page = self.get_page(page_id)
		
		for blob_key in page.files:
			blob_info = blobstore.BlobInfo.get(blob_key)
			
			if blob_info and blob_info.filename == filename:
				return blob_info
		
		return None


# ページの一覧を表示するハンドラ
class PageListHandler(webapp.RequestHandler):
	def get(self):
		
		# ページの一覧を取得
		query = Page.gql(u'ORDER BY id')
		
		# テンプレート引数を用意
		template_values = {
				u'page_list': query
				}
		
		# テンプレートパスを生成
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'page_list.html'
				)
		
		# テンプレートを呼び出す
		self.response.out.write(load_template(self, path, template_values))


# ページの表示
class PageHandler(webapp.RequestHandler):
	def get(self, page_id):
		
		# テンプレートの引数を用意
		template_values = {
				u'page_id': page_id
				}
		
		# ページを取得
		page = util.get_page(page_id)
		
		# ページが存在し、公開されているか、管理者な場合、ページを表示する
		if page and (page.public or util.is_admin()):
			# ページの情報をテンプレート引数に追加
			template_values[u'page_title']    = page.title
			template_values[u'page_text']     = creole2html(page.text)
			template_values[u'page_public']   = page.public
			template_values[u'page_internal'] = page.internal
			
			# 学内限定
			if page.internal:
				template_values[u'page_is_internal'] = \
					util.is_internal(self.request.remote_addr)
			
			# テンプレートのパスを生成
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'page_default.html'
					)
			
		# ページが存在しない場合
		else:
			
			# テンプレートのパスを生成
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'page_none.html'
					)
		
		# テンプレートを呼び出す
		self.response.out.write(load_template(self, path, template_values))


# ページの編集
class PageEditHandler(webapp.RequestHandler):
	
	# ページの編集画面を表示する
	def get(self, page_id):
		
		# テンプレートの引数を用意
		# (ページの情報の初期値)
		template_values = {
				u'page'         : False,
				u'page_id'      : page_id,
				u'page_text'    : u'',
				u'page_title'   : u'',
				u'page_public'  : False,
				u'page_internal': False
				}
		
		# ページを取得
		page = util.get_page(page_id)
		
		# ページが既に存在する場合、内容を取得
		if page:
			template_values[u'page']          = True
			template_values[u'page_text']     = page.text
			template_values[u'page_title']    = page.title
			template_values[u'page_public']   = page.public
			template_values[u'page_internal'] = page.internal
		
		# テンプレートのパスを用意
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'page_edit.html'
				)
		
		# テンプレートを呼び出す
		self.response.out.write(load_template(self, path, template_values))
	
	# ページを保存する
	def post(self, page_id):
		
		# ページのタイトルが指定されて居ない場合は、タイトルとして ID を使用
		title = self.request.get(u'title') or page_id
		
		# テキストが指定されていない場合は nop を使用
		text = self.request.get(u'text') or u'<<nop />>'
		
		# 公開非公開を取得
		public   = self.request.get(u'public')   == u'true'
		internal = self.request.get(u'internal') == u'true'
		
		# ページを取得する
		page = util.get_page(page_id)
		
		# ページが既に存在する場合はページを更新
		if page:
			page.title    = title
			page.text     = text
			page.public   = public
			page.internal = internal
		
		# ページを作成
		else:
			page = Page(
					id       = page_id,
					title    = title,
					text     = text,
					public   = public,
					internal = internal
					)
		
		# データベースを更新
		page.put()
		
		# 書き込んだページへ移動
		self.redirect(u'/page/{0}/'.format(page_id))

# ページの削除
class PageDeleteHandler(webapp.RequestHandler):
	
	# POST メソッドのみ受け入れる
	def post(self, page_id):
		
		# ページを取得
		page = util.get_page(page_id)
		
		# ページが存在するか調べる
		if page is None:
			self.error(404)
			return
		
		# ページの添付ファイルを削除
		for blob_key in page.files:
			blob_info = blobstore.BlobInfo.get(blob_key)
			
			# ファイルが有効な場合
			if blob_info:
				
				# 削除
				blob_info.delete()
		
		# ページを削除
		page.delete()
		
		# 削除済みのページへリダイレクト
		self.redirect(u'/page/{0}/'.format(page_id))


# ページの添付ファイルのページのハンドラ
class PageAttachHandler(blobstore_handlers.BlobstoreUploadHandler):
	
	# 添付ファイル一覧を表示する
	def get(self, page_id):
		
		# テンプレートの引数を用意する
		template_values = {
				u'page_id'   : page_id,
				
				# アップロード先 URL (POST)
				u'upload_url': blobstore.create_upload_url(self.request.path)
				}
		
		# 現在のページを取得
		page = util.get_page(page_id)
		
		# ページが存在しない場合の処理
		if page is None:
			self.error(404)
			return
		
		# 現在添付されているファイルを取得
		upload_files = []
		
		for blob_key in page.files:
			blob_info = blobstore.BlobInfo.get(blob_key)
			
			# ファイルが有効な場合
			if blob_info:
				upload_files.append(blob_info.filename)
		
		# ファイル名一覧をテンプレート引数に追加
		template_values[u'upload_files'] = upload_files
		
		# テンプレートの引数を用意
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'page_attach.html'
				)
		
		# テンプレートを呼び出す
		self.response.out.write(load_template(self, path, template_values))
	
	# 添付ファイルをアップロードする処理
	def post(self, page_id):
		
		# ページを取得する
		page = util.get_page(page_id)
		
		# ページが存在しない場合の処理
		if page is None:
			self.error(404)
			return
		
		# アップロードされたファイルを取得
		upload_files = self.get_uploads(u'file')
		
		# ファイルが存在しない場合
		if not upload_files:
			self.error(400)
			return
		
		# ファイルの情報を取得
		blob_info = upload_files[0]
		
		# ファイルの名前が正しいか調べる
		if not re.compile(ur'[\w\.-]').match(blob_info.filename):
			self.error(400)
			return
		
		# 同名のファイルが存在する場合は削除
		for blob_key in page.files:
			blob_info2 = blobstore.BlobInfo.get(blob_key)
			
			# 同名のファイルが存在する
			if blob_info2 and blob_info.filename == blob_info2.filename:
				blob_info2.delete()
				break
		
		# ファイルのキーを取得
		blob_key = blob_info.key()
		
		# ページのファイル一覧へ追加
		page.files.append(blob_key)
		
		# データベースを更新
		page.put()
		
		# 元のページへリダイレクトする
		self.redirect(self.request.path)

# 添付ファイルを削除するハンドラ
class PageAttachDownloadHandler(
		blobstore_handlers.BlobstoreDownloadHandler,
		PageBaseHandler):
	
	def get(self, page_id, filename):
		page = self.get_page(page_id)
		
		if not page:
			self.redirect('/page/')
			return
		
		filename  = unicode(urllib.unquote(filename), 'utf-8')
		blob_info = self.get_blob(page_id, filename)
		
		if not blob_info:
			self.redirect('/page/{0}/'.format(page_id))
			return
		
		self.send_blob(blob_info)

# ページの添付ファイルの削除
class PageAttachDeleteHandler(PageBaseHandler):
	def post(self, page_id, filename):
		page = self.get_page(page_id)
		
		# ページが存在しない場合
		if not page:
			return self.redirect('/page/')
		
		# ファイルが存在したら削除
		for blob_key in page.files:
			blob_info = blobstore.get(blob_key)
			
			# ファイルが有効かどうか
			if blob_info:
				if  blob_info.filename == filename:
					page.files.remove(blob_key)
					blob_info.delete()
			
			# 無効なファイルは削除
			else:
				page.files.remove(blob_key)
		
		page.put()
		
		return self.redirect('/page/{0}/attach/'.format(page_id))

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
