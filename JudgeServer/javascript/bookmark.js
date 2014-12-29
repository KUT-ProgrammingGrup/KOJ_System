// Last Change: 2012/06/22 14:46:46 +0900.

(function(){
	function insertScript(src, async){
		var element = document.createElement('script');
		
		element.setAttribute("type",    "text/javascript");
		element.setAttribute("charset", "utf-8");
		element.setAttribute("src",     src);
		
		if(async){
			element.setAttribute("async", "async");
		}
		
		var current = document.getElementsByTagName('script')[0];
		current.parentNode.insertBefore(element, current);
	}
	
	// Twitter
	(function(){
		document.write('<a href="https://twitter.com/share" class="twitter-share-button" data-lang="ja" data-related="kut_pg">ツイート</a>');
		
		!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");
	})();
	
	// Facebook
	(function(){
		document.write('<iframe src="//www.facebook.com/plugins/like.php?href=' + encodeURIComponent(location.href) + '&amp;send=false&amp;layout=button_count&amp;width=450&amp;show_faces=false&amp;action=like&amp;colorscheme=light&amp;font&amp;height=21" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:126px; height:21px;" allowTransparency="true"></iframe>');
	})();
	
	// Google+
	(function(){
		document.write('<g:plusone></g:plusone>');
		
		window.___gcfg = {lang: 'ja'};
		
		(function(){ 
			var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
			po.src = 'https://apis.google.com/js/plusone.js';
			var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
		})();
	})();
	
	// はてなブックマーク
	(function(){
		document.write('<a href="http://b.hatena.ne.jp/entry/' + location.href + '" class="hatena-bookmark-button" data-hatena-bookmark-title="' + document.title + '" data-hatena-bookmark-layout="standard" title="このエントリーをはてなブックマークに追加"><img src="http://b.st-hatena.com/images/entry-button/button-only.gif" alt="このエントリーをはてなブックマークに追加" width="20" height="20" style="border: none;" /></a>');
		
		insertScript("http://b.st-hatena.com/js/bookmark_button.js", true);
	})();
})();

// vim: se noet ts=4 sw=4 sts=0 ft=javascript :
