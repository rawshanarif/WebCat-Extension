window.onload=function(){
  chrome.runtime.getBackgroundPage(function(backgroundPage){ 
  var currentUrl = backgroundPage.tabURL;
  //Use the url ........
  console.log(currentUrl);

  document.getElementById('currentUrl').innerHTML = currentUrl;
  
  //document.getElementById('currentUrl').innerHTML='<object type="text/html" data="http://127.0.0.1:5000/post?url="+currentUrl ></object>';

 })

};