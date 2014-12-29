// javascript/attach.js
// 添付ファイル スクリプト

// Last Change: 2011/11/08 16:46:13 +0900.


// ファイルの削除の確認ダイアログを出す
(function(){
	$(document).observe("dom:loaded", function(){
		$$(".content .attach form.delete").each(function(element){
			element.observe("submit", function(event){
				if(!confirm("本当に削除してよろしいですか？")){
					event.stop();
				}
			});
		});
	});
})();


// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
