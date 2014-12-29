#!/usr/bin/python2.7
# coding: utf-8

# Last Change: 2012/06/20 21:50:08 +0900.

# contest.py
# コンテスト用ハンドラ

import os
import json

from datetime import datetime

from google.appengine.ext import webapp

import util

from type import *

# コンテストの一覧を表示するハンドラ
class ContestListHandler(webapp.RequestHandler):
	def get(self):
		
		# コンテストの一覧を取得
		query = Contest.gql(u'ORDER BY start_date ASC')
		
		# コンテストの一覧リストを作成する
		contest_list = []
		
		for contest in query:
			# コンテストが開始しているか調べる
			contest_is_start = contest.start_date and \
					contest.start_date <= datetime.today()
			
			# コンテストが終了しているか調べる
			contest_is_end = contest.end_date and \
					contest.end_date <= datetime.today()
			
			# コンテストの情報をリストに追加
			contest_list.append({
				u'id'        : contest.id,
				u'title'     : contest.title,
				u'start_date': util.to_jst(contest.start_date),
				u'end_date'  : util.to_jst(contest.end_date),
				u'is_start'  : contest_is_start,
				u'is_end'    : contest_is_end,
				u'public'    : contest.public
				})
		
		# テンプレートの引数を用意
		template_values = {
				u'contest_list': contest_list
				}
		
		# テンプレートのパスを生成
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'contest_list.html'
				)
		
		# テンプレートを出力
		self.response.out.write(util.load_template(self, path, template_values))

# コンテストの問題一覧ページのハンドラ
class ContestHandler(webapp.RequestHandler):
	def get(self, contest_id):
		
		# テンプレート引数を用意する
		template_values = {
				u'contest_id'      : contest_id,
				u'contest_is_start': False
				}
		
		# コンテストを取得
		contest = util.get_contest(contest_id)
		
		# コンテストが存在し公開されているか、管理者な場合はコンテストを表示
		if contest and (contest.public or util.is_admin()):
			# コンテストの情報を取得
			template_values[u'contest_title']      = contest.title
			template_values[u'contest_public']     = contest.public
			template_values[u'contest_start_date'] = util.to_jst(contest.start_date)
			template_values[u'contest_end_date']   = util.to_jst(contest.end_date)
			template_values[u'contest_page']       = contest.page
			
			# コンテストが開始しているか調べる
			contest_is_start = contest.start_date and \
					contest.start_date <= datetime.today()
			
			# コンテストが終了しているか調べる
			contest_is_end = contest.end_date and \
					contest.end_date <= datetime.today()
			
			# コンテストが実施中かどうか調べる
			contest_is_playing = contest_is_start and not contest_is_end
			
			# テンプレート引数に追加
			template_values[u'contest_is_start']   = contest_is_start
			template_values[u'contest_is_end']     = contest_is_end
			template_values[u'contest_is_playing'] = contest_is_playing
			
			# 問題の情報を取得する
			problem_list = []
			
			for i in xrange(len(contest.problem)):
				problem = util.get_problem(contest.problem[i])
				
				# 問題の点数情報
				problem_info = {
						u'title'       : None,
						u'num'         : i,
						u'id'          : contest.problem[i],
						u'point_small' : contest.point_small[i],
						u'point_large' : contest.point_large[i]
						}
				
				# 問題の詳細情報
				if problem:
					problem_info.update({
						u'title' : problem.title
						})
				
				problem_list.append(problem_info)
			
			
			template_values[u'contest_problem'] = problem_list
			
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'contest_default.html'
					)
		
		# コンテストが存在しないか、権限が無い場合
		else:
			# テンプレートのパスを生成
			path = os.path.join(
					os.path.dirname(__file__),
					u'template', u'contest_none.html'
					)
		
		
		# テンプレートを描画
		self.response.out.write(util.load_template(self, path, template_values))

# コンテストの問題を開くハンドラ
class ContestProblemHandler(webapp.RequestHandler):
	def get(self, contest_id, problem_id):
		
		# テンプレートの引数を用意
		template_values = {
				u'contest_id': contest_id,
				u'problem_id': problem_id
				}
		
		# コンテストを取得
		contest = util.get_contest(contest_id)
		
		# コンテストが存在しない場合
		if contest is None:
			self.error(404)
			return
		
		# コンテストに問題が存在しない場合
		if int(problem_id) not in contest.problem:
			self.error(404)
			return
		
		# コンテストが開始しているか調べる
		is_contest_start = contest.start_date and \
				contest.start_date <= datetime.today()
		
		# 権限が存在しない場合
		if not util.is_admin() and \
				(not contest.public or not is_contest_start):
					self.error(403)
					return
		
		# コンテストが開始していたら、問題を公開する
		if is_contest_start:
			problem = util.get_problem(problem_id)
			
			# 問題が非公開な場合
			if problem:
				# 公開に設定
				problem.public = True
				
				# データベースを更新
				problem.put()
		
		# 問題のページへリダイレクトする
		self.redirect(u'/problem/{0}/'.format(problem_id))


# コンテストを編集するハンドラ
class ContestEditHandler(webapp.RequestHandler):
	
	# コンテストの編集画面を表示する
	def get(self, contest_id):
		
		# テンプレート引数を用意する (初期値)
		template_values = {
				u'contest'            : False,
				u'contest_id'         : contest_id,
				u'contest_problem'    : u'[]',
				u'contest_point_small': u'[]',
				u'contest_point_large': u'[]'
				}
		
		# コンテストを取得する
		contest = util.get_contest(contest_id)
		
		# コンテストが存在した場合、テンプレート引数に追加
		if contest is not None:
			template_values[u'contest']             = True
			template_values[u'contest_title']       = contest.title
			template_values[u'contest_page']        = contest.page
			template_values[u'contest_public']      = contest.public
			template_values[u'contest_problem']     = json.dumps(contest.problem)
			template_values[u'contest_point_small'] = json.dumps(contest.point_small)
			template_values[u'contest_point_large'] = json.dumps(contest.point_large)
			
			# 開始日時
			if contest.start_date:
				template_values[u'contest_start_date'] = \
					contest.start_date.strftime('%a, %d %b %Y %H:%M:%S UTC')
			
			# 終了日時
			if contest.end_date:
				template_values[u'contest_end_date'] = \
					contest.end_date.strftime('%a, %d %b %Y %H:%M:%S UTC')
		
		# テンプレートのパスを生成する
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'contest_edit.html'
				)
		
		# テンプレートを描画する
		self.response.out.write(util.load_template(self, path, template_values))
	
	# コンテストを編集する
	def post(self, contest_id):
		
		# パラメーターを取得
		title      = self.request.get(u'title')      or contest_id
		page       = self.request.get(u'page')
		start_date = self.request.get(u'start_date') or None
		end_date   = self.request.get(u'end_date')   or None
		public     = self.request.get(u'public') == u'true'
		
		# 日付形式を検証する
		
		# 開始日時の検証
		if start_date is not None:
			try:
				start_date = datetime.strptime(start_date, u'%a, %d %b %Y %H:%M:%S %Z')
			
			except ValueError:
				self.error(400)
				return
		
		# 終了日時の検証
		if end_date is not None:
			try:
				end_date = datetime.strptime(end_date,   u'%a, %d %b %Y %H:%M:%S %Z')
			except ValueError:
				self.error(400)
				return
		
		# 開始日時と終了日時の前後関係を検証する
		if start_date is not None and end_date is not None and \
			start_date > end_date:
				self.error(400)
				return
		
		# 問題のパラメーターの処理
		count       = 0
		problem     = []
		point_small = []
		point_large = []
		
		while self.request.get(u'problem_id_{0}'.format(count)):
			# 問題ID
			try:
				problem_temp = int(self.request.get(u'problem_id_{0}'.format(count)))
			
			except ValueError:
				break
			
			# 点数 (small)
			try:
				point_small_temp = \
					int(self.request.get(u'problem_point_small_{0}'.format(count)))
			
			except ValueError:
				point_small_temp = 0
			
			# 点数 (large)
			try:
				point_large_temp = \
					int(self.request.get(u'problem_point_large_{0}'.format(count)))
			
			except ValueError:
				point_large_temp = 0
			
			problem.append(problem_temp)
			point_small.append(point_small_temp)
			point_large.append(point_large_temp)
			
			# カウンタをインクリメント
			count += 1
		
		# コンテストを取得する
		contest = util.get_contest(contest_id)
		
		# コンテストが既に存在する場合は上書き
		if contest:
			contest.title       = title
			contest.page        = page
			contest.start_date  = start_date
			contest.end_date    = end_date
			contest.problem     = problem
			contest.point_small = point_small
			contest.point_large = point_large
			contest.public      = public
		
		# 存在しない場合は新規作成
		else:
			contest = Contest(
					id          = contest_id,
					title       = title,
					page        = page,
					start_date  = start_date,
					end_date    = end_date,
					problem     = problem,
					point_small = point_small,
					point_large = point_large,
					public      = public
					)
		
		# データベースに反映
		contest.put()
		
		# コンテストの問題一覧ページへ移動
		self.redirect(u'/contest/{0}/'.format(contest_id))

# コンテストのランキングのハンドラ
class ContestRankingHandler(webapp.RequestHandler):
	
	# ランキングを表示する
	def get(self, contest_id):
		
		# コンテストを取得する
		contest = util.get_contest(contest_id)
		
		# コンテストが存在しない場合の処理
		if contest is None:
			self.error(404)
			return
		
		# コンテストが開始されているか調べる
		is_contest_start = contest.start_date and \
				contest.start_date <= datetime.today()
		
		# コンテストが開始されていない場合の処理
		if not is_contest_start:
			self.error(404)
			return
		
		# ランキングをつける
		ranking = {}
		
		query = Answer.gql(u'''
			WHERE problem_id IN :1
				AND date >= :2
				AND date <  :3
			ORDER BY date ASC
		''', contest.problem, contest.start_date, contest.end_date or datetime.today())
		
		for answer in query:
			
			# point_small, point_large
			# 問題が存在しない: 偽
			# 問題が存在する: 真 (正解: 正数, 不正解: 負数)
			if answer.user_id not in ranking:
				ranking[answer.user_id] = {
						u'user_id'    : answer.user_id,
						u'nickname'   : util.get_nickname(answer.user_id),
						u'point_sum'  : 0,
						u'date'       : datetime.utcfromtimestamp(0),
						u'point_small': [ -x if x else x for x in contest.point_small ],
						u'point_large': [ -x if x else x for x in contest.point_large ],
						}
			
			# 問題番号
			num = contest.problem.index(answer.problem_id)
			
			# 問題の情報を追加
			if answer.size == u'small':
				# 問題の点数を取得
				point = int(contest.point_small[num])
				
				if point > 0:
					if ranking[answer.user_id][u'point_small'][num] < 0:
						ranking[answer.user_id][u'point_sum'] += point
					
					ranking[answer.user_id][u'point_small'][num] = point
					
					# 最終提出日時を更新
					ranking[answer.user_id][u'date'] = answer.date
			
			elif answer.size == u'large':
				# 問題の点数を取得
				point = int(contest.point_large[num])
				
				if point > 0:
					if ranking[answer.user_id][u'point_large'][num] < 0:
						ranking[answer.user_id][u'point_sum'] += point
					
					ranking[answer.user_id][u'point_large'][num] = point
					
					# 最終提出日時を更新
					ranking[answer.user_id][u'date'] = answer.date
		
		
		# 辞書をリストに変換
		ranking = ranking.values()
		
		# ランキングをソートする
		def cmp(lhs, rhs):
			if lhs[u'point_sum'] != rhs[u'point_sum']:
				return rhs[u'point_sum'] - lhs[u'point_sum']
			
			return 1 if lhs[u'date'] > rhs[u'date'] else -1
		
		ranking.sort(cmp = cmp)
		
		# ユーザーの情報を整理する
		for i in xrange(len(ranking)):
			ranking[i][u'ranking'] = i + 1
			ranking[i][u'point']   = zip(ranking[i][u'point_small'], ranking[i][u'point_large'])
			
			# タイムゾーンを日本時間に変換
			ranking[i][u'date'] = util.to_jst(ranking[i][u'date'])
		
		# 問題の情報をまとめる
		problem = zip(contest.problem, contest.point_small, contest.point_large)
		
		# テンプレート引数を用意する
		template_values = {
				u'contest_id'         : contest_id,
				u'contest_title'      : contest.title,
				u'contest_problem'    : problem,
				u'contest_ranking'    : ranking
				}
		
		# テンプレートのパスを設定
		path = os.path.join(
				os.path.dirname(__file__),
				u'template', u'contest_ranking.html'
				)
		
		self.response.out.write(util.load_template(self, path, template_values))


# コンテストの削除のハンドラ
class ContestDeleteHandler(webapp.RequestHandler):
	
	# コンテストを削除する
	def post(self, contest_id):
		
		# コンテストを取得
		contest = util.get_contest(contest_id)
		
		# コンテストが存在しない場合
		if contest is None:
			self.error(404)
			return
		
		# コンテストを削除
		contest.delete()
		
		# 削除済みのコンテストへ移動
		self.redirect(u'/contest/{0}/'.format(contest_id))

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
