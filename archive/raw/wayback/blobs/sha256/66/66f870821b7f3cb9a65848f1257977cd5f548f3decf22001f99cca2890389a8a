window.onError=null

var herRef = window.location.href

// if (window == top && self.window.name != "Print") top.location.href = 'http://www.bullseyepistol.com/';

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
function friendlyPrint()  {
window.open(herRef,"Print","scrollbars=1,toolbar=0,menubar=1,status=0,width=630,height=600,resizable=0")
}
function header(big,small,link) {
if (self.window.name != "Print")  {
document.bgColor = '#000028';
document.write("<table border='0' cellspacing='0' width='770' bgcolor='#ffffff'> <tr> <td colspan='2' width='550' bgcolor='#969696'><table border='0' cellpadding='1' cellspacing='0' width='750'> <tr> <td width='750'><a href='javascript:bck()'><font color='#FFFFFF' size='2' face='Tahoma'>&nbsp;<strong>Back Home</strong></font></a><font color='#FFFFFF' size='2' face='Tahoma'><strong> | </strong></font><a href='" + link + "'><font color='#FFFFFF' size='2' face='Tahoma'><strong>Related to this Article</strong></font></a><font color='#FFFFFF' size='2' face='Tahoma'><strong> | </strong></font><a href='alphadex.htm'><font color='#FFFFFF' size='2' face='Tahoma'><strong>Website Index</strong></font></a><font color='#FFFFFF' size='2' face='Tahoma'><strong> | </strong></font><a href='mailto:mail" +"@" + "bullseyepistol.com'><font color='#FFFFFF' size='2' face='Tahoma'><strong>Feedback</strong></font></a><font color='#FFFFFF' size='2' face='Tahoma'><strong> | </strong></font><a href='why.htm'><font color='#FFFFFF' size='2' face='Tahoma'><strong>About this Site</strong></font></a></td> </tr> </table> </td> </tr> <tr> <td colspan='2'><table bgcolor='#ffffff' border='0' cellpadding='2' cellspacing='0' width='740'> <tr> <td width='138' bgcolor='#ffffff'><img src='ebp.gif' width='136' height='100'></td> <td width='500' bgcolor='#ffffff'><font color='#C02F1F' size='5' face='Arial'><em><strong>" + big + "<br> </strong></em></font><font color='#C02F1F' size='3' face='Arial'><em><strong>" + small + "</strong></em></font></td> </tr> </table> </td> </tr> <tr> <td colspan='2' bgcolor='#000080'><font color='#D0D0D0' size='2' face='Tahoma'><strong><a href='javascript:friendlyPrint()'><font color='#D0D0D0' size='2' face='Tahoma'>Click Here for a Printer Friendly Version of this Article</font></a></strong></font></td> </tr> <tr> <td valign='top' bgcolor='#ffffff'>")
}
else {
document.bgColor = '#ffffff';
document.write("</center><p><font color='#C02F1F' size='5' face='Arial'><em><strong>" + big + "<br> </strong></em></font><font color='#C02F1F' size='3' face='Arial'><em><strong>" + small + "</strong></em></font><br><font face='Tahoma' color='#000000' size='2'>www.bullseyepistol.com</font></p>")
}
}

