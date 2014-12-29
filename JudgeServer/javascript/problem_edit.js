
(function(){
	$(document).observe("dom:loaded", function(){
		// キャンセル
		$$(".edit .cancel").first().observe("click", function(){
			location.href = location.href.sub("edit/", "");
		});
		
		// 保存
		$$(".edit form").first().observe("submit", function(event){
			var element = event.element();
			var io_edit = !!$F(element.select('[name="io_edit"]').first());
			
			if(io_edit){
				var input_small  = $F(element.select('[name="input_small"]').first());
				var input_large  = $F(element.select('[name="input_large"]').first());
				var output_small = $F(element.select('[name="output_small"]').first());
				var output_large = $F(element.select('[name="output_large"]').first());
				
				if(
					( input_small && !output_small) ||
					(!input_small &&  output_small) ||
					( input_large && !output_large) ||
					(!input_large &&  output_large)
					)
				{
					alert("エラー: 入力ファイルと出力ファイルはセットで指定してください。");
					event.stop();
				}
			}
		});
		
		// 削除フォーム
		$$(".edit .delete").first().observe("submit", function(event){
			if(!confirm("本当に問題を削除してよろしいですか?")){
				event.stop();
			}
		});
	});
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
