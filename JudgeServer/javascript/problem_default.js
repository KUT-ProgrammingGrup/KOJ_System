
(function(){
	$(document).observe("dom:loaded", function(){
		$$(".submit form").each(function(element){
			element.observe("submit", function(event){
				var element = event.element();
				var output  = !!$F(element.select('[name="output"]').first());
				var source  = !!$F(element.select('[name="source"]').first());
				
				if(!output){
					alert("エラー: 出力ファイルが指定されていません。");
					event.stop();
				}
				
				else if(!source){
					alert("エラー: ソースファイルが指定されていません。");
					event.stop();
				}
			});
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
