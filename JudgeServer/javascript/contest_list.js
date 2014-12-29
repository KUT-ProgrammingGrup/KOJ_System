// javascript/contest_list.js
// コンテスト一覧ページ スクリプト

// Last Change: 2011/11/13 17:40:21 +0900.

(function(){
	$(document).observe("dom:loaded", function(){
		$$(".etc .new").first().observe("click", function(){
			var contest_id = prompt(
				"コンテスト ID を入力してください。\n" +
				"ただし、コンテスト ID は /^[0-9A-Za-z_]+$/ である必要があります。"
				);
			
			// コンテスト ID が入力された場合
			if(contest_id){
				if(contest_id.match(/^\w+$/)){
					location.href = "/contest/" + contest_id + "/edit/";
				}
				
				else {
					alert("コンテスト ID の形式が異なります。");
				}
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
