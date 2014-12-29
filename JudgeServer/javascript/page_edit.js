// javascript/page_edit.js
// ページ編集 スクリプト

// Last Change: 2011/11/08 17:06:39 +0900.

(function(){
	$(document).observe("dom:loaded", function(){
		
		// キャンセルボタン
		$$(".edit .cancel").first().observe("click", function(){
			location.href = location.href.sub("edit/", "");
		});
		
		// 削除フォーム
		$$(".edit .delete").first().observe("submit", function(event){
			if(!confirm("本当にページを削除してよろしいですか?")){
				event.stop();
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
