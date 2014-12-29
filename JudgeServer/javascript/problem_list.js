// javascript/problem_list.js
// 問題一覧ページ スクリプト

// Last Change: 2011/11/13 17:11:27 +0900.

(function(){
	$(document).observe("dom:loaded", function(){
		$$(".etc .new").first().observe("click", function(){
			var problem_id = prompt(
				"問題 ID を入力してください。\n" +
				"ただし、問題 ID は /^[0-9]+$/ である必要があります。"
				);
			
			// 問題 ID が入力された場合
			if(problem_id){
				if(problem_id.match(/^\d+$/)){
					location.href = "/problem/" + problem_id + "/edit/";
				}
				
				else {
					alert("問題 ID の形式が異なります。");
				}
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
