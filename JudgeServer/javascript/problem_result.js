
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
		
		// 解答一覧のリンクを修正する
		if($$(".content .answer").first()){
			(function(){
				var div = $$(".content .answer").first();
				var trs = div.select("tr");
				
				var last_user = null;
				var index     = null;
				
				trs.each(function(tr){
					var user = tr.select("a").first();
					var link = tr.select("a").last();
					
					if(!user || !link) return;
					
					if(last_user != user.innerHTML){
						last_user = user.innerHTML;
						index     = 0;
					}
					
					else {
						++index;
					}
					
					link.href += index + "/";
				});
			})();
		}
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
