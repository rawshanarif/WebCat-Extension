window.onload=function(){
  chrome.runtime.getBackgroundPage(function(backgroundPage){ 
  var currentUrl = backgroundPage.tabURL;
  //Use the url ........
  console.log(currentUrl);

  //document.getElementById('currentUrl').innerHTML = currentUrl;
  
  //document.getElementById('currentUrl').innerHTML='<object type="text/html" data="http://127.0.0.1:5000/post?url=", currentUrl/></object>';

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", 'http://127.0.0.1:5000/post?url='+currentUrl, false ); // false for synchronous request
    xmlHttp.send( null );
	console.log(xmlHttp.responseText);
    document.getElementById('currentUrl').innerHTML = xmlHttp.responseText;
    return xmlHttp.responseText;
      
    var jsonResponse = JSON.parse(xmlHttp.responseText);
    console.log(jsonResponse);
    console.log(jsonResponse[0]);

 })

};
