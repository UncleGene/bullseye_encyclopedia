window.onError=null



// The sold status of upcoming month premium #1 ads =============================================;

var sold = new Object()
 sold[1] = 0
 sold[2] = 0
 sold[3] = 0
 sold[4] = 0
 sold[5] = 0
 sold[6] = 0
 sold[7] = 0
 sold[8] = 0
 sold[9] = 0
sold[10] = 0
sold[11] = 0
sold[12] = 0

// The end of sold status 0 = available, 1 = sold ================================================;

var herRef = window.location.href
var rand = Math.floor(Math.random()*1001)
var ad1 = "redirect1.htm?v=" + rand
var legRef = "advertise3.htm"

function bck() {
var pv = document.referrer;
if (pv.indexOf("index") == -1) {
window.location.href = 'index.htm';
}
else {
window.history.go(-1);
}
}
function Search(field) {
var str = field.findit.value;
var when = new Date();
when.setMonth(when.getMonth() + 1);
var date = when.toGMTString();
document.cookie = "search=" + str + "; expires=" + date + ";path=/";
window.location.href ="search.htm"
}
function changePage(form) {
if (form.jumper.selectedIndex == 0)
return;
else
window.location.href = form.jumper.options[form.jumper.selectedIndex].value;
}
function terms()  {
window.open(legRef,"Print","scrollbars=1,toolbar=0,menubar=1,status=0,width=790,height=600,resizable=0")
}


function header(big,small,link) {

document.bgColor = '#193453'; document.title = big;
document.write("<table style='background-color: rgb(34,149,45); width: 940px;' border='0' cellpadding='0' cellspacing='0'><tr><td colspan='1' rowspan='2' style='background-color: rgb(34, 149, 45);'><img style='width: 144px; height: 122px;' alt='Logo' src='pagelogo.jpg'></td><td><table width='100%' border='0' cellpadding='0' cellspacing='0'><td colspan='1' background='cutout2.jpg?v=2' style='font-family: Tahoma; font-size: 10px; font-weight: bold; color: #debea1; text-align: center; background-color: rgb(34, 149, 45); height: 22px; width: 790px;'>&nbsp;<a style='color: #debea1;' href='javascript:bck()'>Back Home</a> | <a style='color: #debea1;' href='" + link + "'>Related to this Article</a> | <a href='alphadex.htm' style='color: #debea1;'>Website Index</a> | <a style='color: #debea1;' href='mailto:mail@bullseyepistol.com'>Feedback</a> | <a style='color: #debea1;' href='why.htm'>About this Site</a></td><td style='width: 22px;'><img src='topright.jpg' width='22' height='22' border='0'></td></tr></table></td></tr><tr><td style='height: 100px;' colspan='1' style='background-color: rgb(34, 149, 45);'><table style='width:100%;'><tr><td style='color: #edd3b7; font-family: Arial; font-size: 24px; font-style: italic; font-weight: bold; vertical-align:middle;' style='width:740px;'>&nbsp; " + big + "</div><div style='color: #edd3b7; font-family: Arial; font-size: 16px; font-style: italic; font-weight: bold;'>&nbsp; &nbsp; " + small + "</td><td><a href='" + ad1 + "'><img src='premium1.jpg?v=" + rand + "' align='right' border='0'></a></td></tr></table></td></tr><tr><td colspan='2' rowspan='1' background='roundbar1.jpg' style='background-color: rgb(34, 149, 45); height:27px;'>&nbsp;<a href='javascript:bck()' style='font-family: Tahoma; font-size: 13px; color: rgb(240, 240, 224);'>Abort the Process of Ordering Advertising</a></td></tr></table><table border='0' cellpadding='0' cellspacing='3' style='background-color: #ffffff; width: 940px;'><tr><td bgcolor='#ffffff' valign='top' style='width:744px;'>")

}


