#!/usr/bin/env python2.7
# coding: utf-8
# Last Change: 2011/11/15 13:34:52 +0900.

import os
import re
import cgi
import mimetypes
import time

from google.appengine.ext        import webapp
from google.appengine.api        import users
from google.appengine.ext.webapp import blobstore_handlers

import util

from type import *
from util import *

# 問題のベースハンドラ
class ProblemBaseHandler(webapp.RequestHandler):
	
	# 問題を取得する
	def get_problem(self, problem_id):
		query   = Problem.gql(u'WHERE id = :1', int(problem_id))
		problem = query.get()
		
		return problem
	
	# 解答を取得
	def get_answer(self, problem_id, size, user_id):
		query = Answer.gql(u'''
			WHERE problem_id = :1
				AND user_id = :2
				AND size = :3
			ORDER BY date DESC''',
				int(problem_id),
				user_id,
				size)
		
		answer = query.get()
		
		return answer


# 問題の一覧を表示するハンドラ
class ProblemListHandler(webapp.RequestHandler):
	def get(self):
		query        = Problem.gql(u'ORDER BY id')
		problem_list = query if query.count() > 0 else None 
		
		template_values = {
				u'problem_list': problem_list
				}
		
		path = os.path.join(
				os.path.dirname(__file__),
				'template', 'problem_list.html'
				)
		
		self.response.out.write(load_template(self, path, template_values))
		

# 問題を表示するハンドラ
class ProblemHandler(ProblemBaseHandler):
	def get(self, problem_id):
		
		template_values = {
				u'problem_id': problem_id
				}
		
		problem = self.get_problem(problem_id)
		
		# 問題が存在し公開されている場合か、管理者な場合は問題を表示
		if problem and (problem.public or users.is_current_user_admin()):
			template_values[u'problem_title']   = problem.title
			template_values[u'problem_text']    = creole2html(problem.text)
			template_values[u'problem_public']  = problem.public
			template_values[u'problem_small']   = problem.input_small is not None
			template_values[u'problem_large']   = problem.input_large is not None
			
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'problem_default.html'
					)
		
		else:
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'problem_none.html'
					)
		
		self.response.out.write(load_template(self, path, template_values))

# 問題の入力ファイルのダウンロード
class ProblemDownloadHandler(ProblemBaseHandler):
	def get(self, problem_id, size, type):
		
		# テキストファイルに設定
		self.response.headers[u'Content-Type'] = u'text/plain'
		
		# 問題を取得
		problem = self.get_problem(problem_id)
		
		# 問題が存在しない場合
		if not problem:
			self.error(404)
			return
		
		# ファイル別に処理
		if (size, type) == (u'small', u'in'):
			if problem.input_small:
				self.response.out.write(problem.input_small)
				return
			
			else:
				self.error(404)
				return
			
		elif (size, type) == (u'large', u'in'):
			if problem.input_large:
				self.response.out.write(problem.input_large)
				return
			
			else:
				self.error(404)
				return
		
		elif (size, type) == (u'small', u'out'):
			if problem.output_small:
				self.response.out.write(problem.output_small)
				return
			
			else:
				self.error(404)
				return
		
		else:
			if problem.output_large:
				self.response.out.write(problem.output_large)
				return
			
			else:
				self.error(404)
				return


# 問題の編集
class ProblemEditHandler(ProblemBaseHandler):
	def get(self, problem_id):
		
		# テンプレートに渡す引数を用意
		template_values = {
				u'problem'   : False,
				u'problem_id': problem_id
				}
		
		# 問題を取得
		problem = self.get_problem(problem_id)
		
		# 問題が既に存在する場合、テンプレート引数に追加
		if problem:
			template_values[u'problem']        = True
			template_values[u'problem_title']  = problem.title
			template_values[u'problem_text']   = problem.text
			template_values[u'problem_public'] = problem.public
			template_values[u'problem_small']  = problem.input_small is not None
			template_values[u'problem_large']  = problem.input_large is not None
		
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'problem_edit.html'
				)
		
		self.response.out.write(load_template(self, path, template_values))
	
	# 問題の編集
	def post(self, problem_id):
		
		# 問題のタイトルが指定されていない場合、問題 id を使用する
		title   = self.request.get(u'title') or problem_id
		text    = self.request.get(u'text')
		public  = self.request.get(u'public')  == u'true'
		io_edit = self.request.get(u'io_edit') == u'true'
		
		if io_edit:
			
			# 入出力ファイルの処理
			input_small  = self.request.get(u'input_small')
			input_large  = self.request.get(u'input_large')
			output_small = self.request.get(u'output_small')
			output_large = self.request.get(u'output_large')
			
			# 改行コードを統一する
			if input_small and output_small:
				input_small  = to_line_feed(input_small)
				output_small = to_line_feed(output_small)
			
			else:
				input_small  = None
				output_small = None
			
			if input_large and output_large:
				input_large  = to_line_feed(input_large)
				output_large = to_line_feed(output_large)
			
			else:
				input_large  = None
				output_large = None

		# 問題を取得
		problem = self.get_problem(problem_id)
		
		# 問題が存在する場合は問題を更新
		if problem:
			problem.title        = title
			problem.text         = text
			problem.public       = public
			
			if io_edit:
				problem.input_small  = input_small
				problem.input_large  = input_large
				problem.output_small = output_small
				problem.output_large = output_large
			
		# 問題が存在しない場合は、問題を新規作成
		else:
			problem = Problem(
					id     = int(problem_id),
					title  = title,
					text   = text,
					public = public
					)
			
			if io_edit:
				problem.input_small  = input_small
				problem.input_large  = input_large
				problem.output_small = output_small
				problem.output_large = output_large
		
		problem.put()
		
		self.redirect(u'/problem/{0}/reload/{1}/'.format(
			problem_id, int(time.time())
			))

# 問題を提出するハンドラ
class ProblemSubmitHandler(ProblemBaseHandler):
	def post(self, problem_id, size):
		
		# 問題を取得する
		problem = self.get_problem(problem_id)
		
		# 問題が存在しない場合の処理
		if not problem:
			self.error(404)
			return
		
		# 問題に指定サイズの入出力ファイルが存在しない場合の処理
		if size == u'small' and not problem.input_small:
			self.error(404)
			return
		
		if size == u'large' and not problem.input_large:
			self.error(404)
			return
		
		# ソースファイルが指定されていない場合の処理
		if u'source' not in self.request.POST or \
				not isinstance(self.request.POST[u'source'], cgi.FieldStorage):
					self.error(400)
					return
		
		# 出力ファイルを取得
		output = self.request.get(u'output')
		
		# 改行コードを統一
		output = to_line_feed(output)
		
		# 解答の正誤を調べる
		if size == u'small':
			result = (output == problem.output_small)
		
		else:
			result = (output == problem.output_large)
		
		# 正答だった場合、データベースに反映
		if result:
			
			# ソースファイルを取得
			source = self.request.get(u'source')
			
			# 出力ファイルのファイル名を取得
			filename = self.request.POST[u'source'].filename
			
			# 解答が存在しない場合、新規作成
			answer = Answer(
					user_id    = users.get_current_user().user_id(),
					problem_id = int(problem_id),
					size       = size,
					filename   = filename,
					source     = source
					)
			
			# データベースに保存
			answer.put()
		
		# 結果ページへリダイレクトする
		self.redirect(u'/problem/{0}/result/'.format(problem_id))

# 問題の結果を表示する
class ProblemResultHandler(ProblemBaseHandler):
	def get(self, problem_id):
		
		template_values = {
				u'problem_id':   problem_id
				}
		
		problem = self.get_problem(problem_id)
		
		# 問題が存在し公開されている場合か、管理者な場合は問題を表示
		if problem and (problem.public or users.is_current_user_admin()):
			
			# 問題の情報を取得
			template_values[u'problem_title']   = problem.title
			template_values[u'problem_text']    = creole2html(problem.text)
			template_values[u'problem_public']  = problem.public
			template_values[u'problem_small']   = problem.input_small is not None
			template_values[u'problem_large']   = problem.input_large is not None
			
			# ログインしている場合は、判定を取得
			if users.get_current_user() is not None:
				
				# small の結果を取得
				if problem.input_small is not None:
					answer_small = util.get_answer(
							problem_id = problem_id,
							size       = u'small',
							user_id    = users.get_current_user().user_id()
							).get()
					
					if answer_small:
						template_values[u'answer_small'] = {
								u'date': util.to_jst(answer_small.date)
								}
				
				# large の結果を取得
				if problem.input_large is not None:
					answer_large = util.get_answer(
							problem_id = problem_id,
							size       = u'large',
							user_id    = users.get_current_user().user_id()
							).get()
					
					if answer_large:
						template_values[u'answer_large'] = {
								u'date': util.to_jst(answer_large.date)
								}
			
			
			# 管理者な場合は、回答一覧を取得
			if users.is_current_user_admin():
				query = util.get_answer(problem_id)
				
				answer_list = []
				
				for answer in query:
					answer_list.append({
						u'size'    : answer.size,
						u'nickname': get_nickname(answer.user_id),
						u'user_id' : answer.user_id,
						u'filename': answer.filename,
						u'date'    : util.to_jst(answer.date)
						})
				
				template_values[u'answer_list'] = answer_list

			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'problem_result.html'
					)
		
		# 問題が存在しないか、非公開な場合
		else:
			self.error(404)
			
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'problem_none.html'
					)
		
		self.response.out.write(load_template(self, path, template_values))

# ソースファイルのダウンロード
class ProblemSourceDownloadHandler(ProblemBaseHandler):
	def get(self, problem_id, user_id, size, offset):
		
		# 問題を取得する
		problem = self.get_problem(problem_id)
		
		# 問題が存在しない場合
		if not problem:
			self.error(404)
			return

		# 解答を取得する
		query = util.get_answer(
				problem_id = problem_id,
				user_id    = user_id,
				size       = size
				)
		
		answer = query.fetch(1, int(offset))
		
		# 解答が存在しない場合
		if not answer:
			self.error(404)
			return
		
		else:
			answer = answer[0]
		
		# ファイルタイプを求める
		mimetype = mimetypes.guess_type(answer.filename)[0]
		
		if not mimetype:
			mimetype = u'application/octet-stream'
		
		# HTTP ヘッダを作成
		self.response.headers[u'Content-Type']        = mimetype
		self.response.headers[u'Content-Disposition'] = \
			u'attachment; filename="{0}"'.format(answer.filename)
		
		# ファイルの内容を出力
		self.response.out.write(answer.source)


# 問題の添付ファイルのハンドラ
class ProblemAttachHandler(ProblemBaseHandler, blobstore_handlers.BlobstoreUploadHandler):
	
	# 添付ファイルの一覧と、アップロードフォームの表示
	def get(self, problem_id):
		
		# テンプレートの引数を用意する
		template_values = {
				u'problem_id': problem_id,
				
				# アップロード先 URL を取得する (POST)
				u'upload_url': blobstore.create_upload_url(self.request.path)
				}
		
		# 現在の問題を取得
		problem = util.get_problem(problem_id)
		
		# 問題が存在しない場合
		if not problem:
			self.error(404)
			return
		
		# 添付ファイルの一覧を取得する
		upload_files = []
		
		for blob_key in problem.files:
			# ファイルの実体を取得する
			blob_info = blobstore.BlobInfo.get(blob_key)
			
			# ファイルが存在する場合、一覧に追加
			if blob_info:
				upload_files.append(blob_info.filename)
		
		# テンプレート引数にファイルの一覧を追加
		template_values[u'upload_files'] = upload_files
		
		# テンプレートのパスを生成する
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'problem_attach.html'
				)
		
		# テンプレートｗ書きだす
		self.response.out.write(util.load_template(self, path, template_values))
	
	# ファイルアップロード後の処理
	def post(self, problem_id):
		
		# 問題を取得
		problem = util.get_problem(problem_id)
		
		# 問題が存在しない場合の処理
		if not problem:
			self.error(404)
			return
		
		# アップロードされたファイル一覧を取得
		upload_files = self.get_uploads('file')
		
		# ファイルが存在しない場合
		if not upload_files:
			self.error(400)
			return
		
		# ファイルを取得
		blob_info = upload_files[0]
		
		# ファイルの名前が正しくない場合の処理
		if not re.compile(ur'[\w\.-]').match(blob_info.filename):
			
			# データを削除
			blob_info.delete()
			
			self.error(400)
			return
		
		
		# 同名のファイルが存在する場合は、古い方を削除
		for blob_key in problem.files:
			# ファイルの情報を取得
			blob_info_old = blobstore.BlobInfo.get(blob_key)
			
			# 同名な場合は削除
			if blob_info_old and blob_info.filename == blob_info_old.filename:
				blob_info_old.delete()
		
		# ファイルを識別するキーを取得
		blob_key = blob_info.key()
		
		# 問題のファイル一覧に追加
		problem.files.append(blob_key)
		
		# データベースを更新
		problem.put()
		
		# 一覧ページへリダイレクト
		self.redirect(self.request.path)

# 問題の添付ファイルをダウンロードするハンドラ
class ProblemAttachDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, problem_id, filename):
		
		# 問題を取得
		problem = util.get_problem(problem_id)
		
		# 問題が存在しない場合の処理
		if problem is None:
			self.error(404)
			return
		
		# ファイルを取得
		blob_info = util.get_problem_blob(problem_id, filename)
		
		# ファイルが存在しない場合
		if blob_info is None:
			self.error(404)
			return
		
		# ファイルを送信する
		self.send_blob(blob_info)

# 問題の添付ファイルを削除するハンドラ
class ProblemAttachDeleteHandler(webapp.RequestHandler):
	
	# POST のみ受け付ける
	def post(self, problem_id, filename):
		
		# 問題を取得
		problem = util.get_problem(problem_id)
		
		# 問題が存在しない場合
		if problem is None:
			self.error(400)
			return
		
		# ファイルが正常に削除されたかどうか
		is_deleted = False
		
		# 問題から削除するファイルのキー
		delete_key = []
		
		# ファイルが存在したら削除
		for blob_key in problem.files:
			
			# ファイルの情報を取得
			blob_info = blobstore.get(blob_key)
			
			# ファイルが無効な場合
			if blob_info is None:
				
				# 削除するファイルとして記憶
				delete_key.append(blob_key)
			
			# ファイル名が一致した場合
			elif blob_info and blob_info.filename == filename:
				
				# 削除するファイルとして記憶
				delete_key.append(blob_key)
				
				# ファイルの実体を削除
				blob_info.delete()
				
				# ファイルの削除に成功として記憶
				is_deleted = True
		
		# 問題にファイルの削除を反映
		for blob_key in delete_key:
			problem.files.remove(blob_key)
		
		# データベースに反映
		problem.put()
		
		# ファイルの削除が失敗した場合、エラーコードを返す
		if not is_deleted:
			self.error(400)
			return
		
		# ファイルの一覧ページへ移動
		return self.redirect('/problem/{0}/attach/'.format(problem_id))

# 問題を削除するハンドラ
class ProblemDeleteHandler(webapp.RequestHandler):

	# 問題を削除する
	def post(self, problem_id):
		
		# 問題を取得
		problem = util.get_problem(problem_id)
		
		# ページが存在するか調べる
		if problem is None:
			self.error(404)
			return
		
		# ページの添付ファイルを削除
		for blob_key in problem.files:
			blob_info = blobstore.BlobInfo.get(blob_key)
			
			# ファイルが有効な場合
			if blob_info:
				
				# 削除
				blob_info.delete()
		
		# 解答を取得
		query = util.get_answer(problem_id)
		
		# 解答を削除
		for answer in query:
			answer.delete()
		
		# 問題を削除
		problem.delete()
		
		# 削除済みの問題へリダイレクト
		self.redirect(u'/problem/{0}/'.format(problem_id))

# キャッシュ対策の為、問題をリロード
class ProblemReloadHandler(webapp.RequestHandler):
	def get(self, problem_id):
		self.redirect(u'/problem/{0}/'.format(problem_id))

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
