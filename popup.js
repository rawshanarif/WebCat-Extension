
window.onload=function(){

  document.getElementById("loading").style.display;

  chrome.runtime.getBackgroundPage(function(backgroundPage){ 
  var currentUrl = backgroundPage.tabURL;
  console.log(currentUrl);
  
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", 'http://127.0.0.1:5000/post?url='+currentUrl, false ); // false for synchronous request
  xmlHttp.send( null );
  console.log(xmlHttp.responseText);
  document.getElementById('currentUrl').innerHTML = xmlHttp.responseText;

  var jsonResponse = JSON.parse(xmlHttp.responseText);
  var ranking = (jsonResponse[0]);
  var keywords = (jsonResponse[1]);

  console.log(jsonResponse);
  console.log(jsonResponse[0]);
  console.log(jsonResponse[1]);

  document.getElementById("title1").textContent = "Potential Article Bias:";

  if (ranking == "FarLeft")
    document.getElementById("farleft").textContent = "Far Left";

  else if (ranking == "Left")
    document.getElementById("left").textContent = "Left";

  else if (ranking == "LeanLeft")
    document.getElementById("leanleft").textContent = "Lean Left";

  else if (ranking == "Neutral")
    document.getElementById("neutral").textContent = "Neutral";

  else if (ranking == "LeanRight")
    document.getElementById("leanright").textContent = "Lean Right";

  else if (ranking == "Right")
    document.getElementById("right").textContent = "Right";

  else if (ranking == "FarRight")
    document.getElementById("farright").textContent = "Far Right";

  else if (ranking == "Undetermined")
    document.getElementById("undetermined").textContent = "Undetermined";
	
  else {document.getElementById("error").textContent = "Sorry, an error was encountered";}
	
  document.getElementById("loading").style.display = "none";

  document.getElementById("title2").textContent = "Top Contributing Words/Phrases";

  document.getElementById("currentUrl").style.display = "none";

  document.getElementById("topwords").textContent = jsonResponse[1];

  //return xmlHttp.responseText;

 })

}


