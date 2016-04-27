<?php
$ch = curl_init();
$retry = 3;
while ( (!$retry) || $word = fgets(STDIN)) {
	$url = "https://ac.duckduckgo.com/ac/?callback=autocompleteCallback&_=1461001571433&q=".trim($word);
	$proxy = '127.0.0.1:8899';
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_PROXY, $proxy);
	$headers = array('accept-encoding: gzip, deflate, sdch', 'accept-language: en-US,en;q=0.8', 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36', 'accept: */*', 'referer: https://duckduckgo.com/');
	curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
	$response = curl_exec($ch);
	if (!$response) {
		$ch = curl_init();
		$retry -= 1;
	} 
	else 
	{
		$retry = 3;
		echo($word);
	}
}
curl_close ($ch);

