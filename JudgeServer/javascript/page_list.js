// javascript/page_list.js
// ページ一覧ページ スクリプト

// Last Change: 2011/11/13 17:17:54 +0900.

(function(){
	$(document).observe("dom:loaded", function(){
		$$(".etc .new").first().observe("click", function(){
			var page_id = prompt(
				"ページ ID を入力してください。\n" +
				"ただし、ページ ID は /^[0-9A-Za-z_]+$/ である必要があります。"
				);
			
			// ページ ID が入力された場合
			if(page_id){
				if(page_id.match(/^\w+$/)){
					location.href = "/page/" + page_id + "/edit/";
				}
				
				else {
					alert("ページ ID の形式が異なります。");
				}
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
