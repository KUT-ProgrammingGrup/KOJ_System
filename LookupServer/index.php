<?php
	error_reporting(-1);
	
	$url  = 'http://wikiwiki.jp/kut-pg/';
	
	$headers = getallheaders();
	$addr    = @$headers['X-Remote-Addr'];
	
	function redirect(){
		global $url;
		
		header('Location: '.$url);
	}
	
	if(empty($addr)){
		redirect();
	}
	
	else {
		$host = gethostbyaddr($addr);
		
		if($host === false || $host == $addr){
			redirect();
		}
		
		else {
			header('X-Remote-Host: '.$host);
		}
	}
?>
