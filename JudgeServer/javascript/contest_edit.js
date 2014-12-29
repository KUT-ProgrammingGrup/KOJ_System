// Last Change: 2011/11/14 17:32:15 +0900.

// javascript/contest_edit.js
// コンテスト編集ページ スクリプト

(function(){
	$(document).observe("dom:loaded", function(){
		
		// 問題の通し番号を再計算する関数
		function changeProblemNumber(){
			var elements = $$(".edit .problem > div");
			
			elements.each(function(element, index){
				// タイトルを変更
				var title = element.select(".title").first();
				title.innerHTML = title.innerHTML.replace(/\d+/, index);
				
				// 各種コントロールを変更
				element.select('input[type="text"]').each(function(element2){
					element2.name = element2.name.replace(/\d+/, index);
				});
			});
		}
		
		// 問題を追加する関数
		// 戻り値: 追加した問題の要素
		function addProblem(){
			var template = $($$(".edit .problem_template").first().cloneNode(true));
			var parent   = $$(".edit .problem").first();
			
			// テンプレートを可視化
			template.removeClassName("problem_template");
			
			// 入力フォームを有効化する
			template.select("input").each(function(element){
				element.removeAttribute("disabled");
			});
			
			// 削除ボタンにイベントを設定
			template.select(".delete").first().observe("click", function(){
				if(window.confirm("本当に削除してよろしいですか?")){
					
					// 要素を削除
					parent.removeChild(template);
					
					changeProblemNumber();
				}
			});
			
			// 要素を追加
			parent.appendChild(template);
			
			// 問題の通し番号を再計算する
			changeProblemNumber();
			
			return template;
		}
		
		// IETF 標準時刻構文に変換
		function dateToIETF(date){
			var months = [
				"Jan",
				"Feb",
				"Mar",
				"Apr",
				"May",
				"Jun",
				"Jul",
				"Aug",
				"Sep",
				"Oct",
				"Nov",
				"Dec"
				];
			
			var days = [
				"Sun",
				"Mon",
				"Tue",
				"Wed",
				"Thu",
				"Fri",
				"Sat"
				];
			
			return days[date.getUTCDay()] + ", " +
				("00" + date.getUTCDate()).slice(-2) + " " +
				months[date.getUTCMonth()] + " " +
				date.getUTCFullYear() + " " +
				("00" + date.getUTCHours()).slice(-2) + ":" +
				("00" + date.getUTCMinutes()).slice(-2) + ":" +
				"00" + " " + "UTC";
		}
		
		// 日付を要素から取得
		function getDateFromElement(element){
			// 日本時間を UTC として日付オブジェクトを作成
			var date = new Date();
			
			var year_value   = $F(element.select(".year").first());
			var month_value  = $F(element.select(".month").first());
			var date_value   = $F(element.select(".date").first());
			var hour_value   = $F(element.select(".hour").first());
			var minute_value = $F(element.select(".minute").first());
			
			if(year_value && month_value && date_value && hour_value && minute_value){
				date.setUTCFullYear(year_value);
				date.setUTCMonth(month_value - 1);
				date.setUTCDate(date_value);
				date.setUTCHours(hour_value);
				date.setUTCMinutes(minute_value);
				
				// UTC に変換
				date.setTime(date.getTime() - 9 * 60 * 60 * 1000);
				
				return dateToIETF(date);
			}
			
			return "";
		}
		
		// 問題の初期値を設定する
		(function(){
			for(var i = 0; i < contest_problem.length; ++i){
				(function(){
					var problem = addProblem();
					
					problem.select('[name^="problem_id"]').first().value =
						contest_problem[i];
					
					problem.select('[name^="problem_point_small"]').first().value =
						contest_point_small[i];
					
					problem.select('[name^="problem_point_large"]').first().value =
						contest_point_large[i];
				})();
			}
		})();
		
		// 日付を設定
		(function(){
			$$(".edit p.date").each(function(element){
				// 日付を取得
				var date_value = $F(element.select('[name$="date"]').first());
				
				// 日付が設定されている場合
				if(date_value){
					// 日付オブジェクトをローカルタイムで作成
					var date = new Date(date_value);
					
					// 環境によらず JST として扱うため、UTC から変換
					// 内部時間 (UTC) を JST として処理する
					date.setTime(date.getTime() + 9 * 60 * 60 * 1000);
					
					element.select(".year").first().value   = date.getUTCFullYear();
					element.select(".month").first().value  = date.getUTCMonth() + 1;
					element.select(".date").first().value   = date.getUTCDate();
					element.select(".hour").first().value   = date.getUTCHours();
					element.select(".minute").first().value = date.getUTCMinutes();
				}
			});
		})();
		
		// 問題の追加ボタンのイベント
		$$(".edit .add_problem").first().observe("click", function(){
			addProblem();
		});
		
		// キャンセルボタン
		$$(".edit .cancel").first().observe("click", function(){
			location.href = location.href.sub("edit/", "");
		});
		
		// 送信時の処理
		$$(".edit form").first().observe("submit", function(event){
			// 日付の検証
			$$(".edit p.date").each(function(element){
				element.select('[name$="date"]').first().value =
					getDateFromElement(element);
			});
		});
		
		// 削除フォーム
		$$(".edit form.delete").first().observe("submit", function(event){
			if(!confirm("本当にコンテストを削除してよろしいですか?")){
				event.stop();
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
