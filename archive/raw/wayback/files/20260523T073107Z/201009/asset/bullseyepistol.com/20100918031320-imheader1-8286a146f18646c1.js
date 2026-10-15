window.onError=null;
if (window == top) top.location.href = 'http://www.ilmoleague.com/';

var loc = new Object()
loc[0] = "imnews.htm"
loc[1] = "imhist.htm"
loc[2] = "imrecord.htm"
loc[3] = "imstand.htm"
loc[4] = "imprev.htm"
loc[5] = "imbylaws.htm"
loc[6] = "imteams.htm"
loc[7] = "imadmin.htm"
loc[8] = "imforms.htm"
loc[9] = "imsoft.htm"
loc[10] = "mailto:president" + "@" + "ilmoleague.com"

function eMail1() {
var pb="ilmoleague.com";
var pa="president";
var pc=pa + "@" + pb;
document.write("<a href='mailto:" + pc + "'><font size='4' face='Tahoma'><strong>President:</strong></font></a>");
}
function eMail2() {
var pb="ilmoleague.com";
var pa="president";
var pc=pa + "@" + pb;
document.write("<a href='mailto:" + pc + "'><font size='4' face='Tahoma'><strong>John Dreyer</strong></font></a>");
}
function mOver(p) {
p.style.backgroundColor='#0000a0';
p.style.cursor='hand';
}
function mOut(p) {
p.style.backgroundColor='#0181CD';
p.style.cursor='hand';
}
function header(title) {
document.write("<table border='0' cellpadding='2' cellspacing='0' width='770'> <tr> <td colspan='3' width='770' bgcolor='#909090' class='nav'>&nbsp; <a href='ilmo.htm'>Home</a> | <a href='imnews.htm'>News</a> | <a href='imhist.htm'>History</a> | <a href='imrecord.htm'>Records</a> | <a href='mailto:president" + "@" + "ilmoleague.com'>Contact</a></td> </tr> <tr> <td colspan='3'><img src='spacer.gif' width='766' height='1'></td> </tr> <tr> <td align='center' width='170'><img src='illmo.gif' width='130' height='127'></td> <td align='center' width='430' class='hed'><b>" + title + "</b></td> <td align='center' width='170'><img src='nrasactioned.gif' width='130' height='127'></td> </tr> <tr> <td><img src='spacer.gif' width='168' height='1'></td> <td><img src='spacer.gif' width='428' height='1'></td> <td><img src='spacer.gif' width='168' height='1'></td> </tr></table><table border='0' cellpadding='2' cellspacing='0' width='770'> <tr> <td colspan='2' bgcolor='#282E80'><font color='#C0C0C0' size='2' face='Tahoma'>The Focal Point of Pistol Competition in the St. Louis Area Since 1949!</font></td> </tr> <tr> <td width='580' bgcolor='#D6E9FC' class='art'>")
}
function footer() {
document.write("</td> <td align='center' valign='top' bgcolor='#7C9BD6'><table border='1' cellpadding='0' cellspacing='0' width='188' bgcolor='#0181CD' bordercolor='#029BF7' bordercolordark='#9CDAFE' bordercolorlight='#025A8E'> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[0]' onmouseout='mOut(this)'>&nbsp;<a href='imnews.htm'>News &amp; Events</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[1]' onmouseout='mOut(this)'>&nbsp;<a href='imhist.htm'>League History</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[2]' onmouseout='mOut(this)'>&nbsp;<a href='imrecord.htm'>League Records</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[3]' onmouseout='mOut(this)'>&nbsp;<a href='imstand.htm'>Current Standings</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[4]' onmouseout='mOut(this)'>&nbsp;<a href='imprev.htm'>Previous Seasons</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[5]' onmouseout='mOut(this)'>&nbsp;<a href='imbylaws.htm'>Organization Bylaws</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[6]' onmouseout='mOut(this)'>&nbsp;<a href='imteams.htm'>Participating Teams</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[7]' onmouseout='mOut(this)'>&nbsp;<a href='imadmin.htm'>League Officers</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[8]' onmouseout='mOut(this)'>&nbsp;<a href='imforms.htm'>Download Forms</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onclick='location.href=loc[9]' onmouseout='mOut(this)'>&nbsp;<a href='imsoft.htm'>Download Software</a></td> </tr> <tr> <td class='but' onmouseover='mOver(this)' onmouseout='mOut(this)'>&nbsp;<a href='mailto:president@ilmoleague.com'>Contact President</a> </td> </tr> </table> <p align='center'> </p>  </td> </tr> <tr> <td colspan='2' bgcolor='#282E80'><font color='#C0C0C0' size='2' face='Tahoma'>This Donated Website is Solely Designed, Maintained and Owned by League President, John A. Dreyer, &copy; 2007 </font></td> </tr> <tr> <td width='570'><img src='spacer.gif' width='568' height='1'></td> <td width='200'><img src='spacer.gif' width='198' height='1'></td> </tr></table>")
}