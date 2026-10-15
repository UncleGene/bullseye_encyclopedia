var rand = Math.floor(Math.random()*1001)
var ad2 = "redirect2.htm?v=" + rand
var ad3 = "redirect3.htm?v=" + rand

var color1 = "#3265a3"
var color2 = "#072f61"
var loc = new Object()
loc[0] = "index.htm"
loc[1] = "alphadex.htm"
loc[2] = "amucover.htm"
loc[3] = "http://bullseyepistol.forumotion.com/"
loc[4] = "links.htm#clubs"
loc[5] = "links.htm#directory"
loc[6] = "links.htm#products"
loc[7] = "other.htm"
loc[9] = "zeninfo.htm"
loc[10] = "rangecmd.htm"
loc[11] = "why.htm"

function mOver(p) {
p.style.backgroundColor='#072f61';
}
function mOut(p) {
p.style.backgroundColor='#3265a3';
}

function footer()  {
if (self.window.name != "Print")  {
document.write("</td><td valign='top' align='center'><form action='NOACTION'> <table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#8eb3d8'> <tr> <td><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Search This Site:</div><input type='text' size='13' maxlength='18' name='findit'> <input type='button' value='Find' onclick='Search(this.form)'><br> <div style='font-family: arial; font-size: 11px;'>(One word works best)<br> <br> </div><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Site Quickstart:</div><select name='jumper' size='1' onchange='changePage(this.form)'> <option selected value>Select Topic</option> <option value='alphadex.htm'>Website Index</option> <option value='amucover.htm'>USAMU Manual</option> <option value='http://www.nrahq.org/compete/RuleBooks/Pistol/pst-index.pdf'>NRA Rule Book</option> <option value='zeninfo.htm'>Zen in Shooting</option> <option value='rangecmd.htm'>Range Commands</option> <option value='http://bullseyepistol.forumotion.com/'>Bullseye-L Forum</option> <option value='links.htm#clubs'>Clubs &amp; Teams</option> <option value='other.htm'>Other Disciplines</option> <option value='why.htm'>About This Site</option> <option value='index.htm'>Back Home</option> </select><input type='button' value='Go' onclick='changePage(this.form)'></td></tr></table>");

document.write("<table bgcolor='#8eb3d8' border='0' cellpadding='2' cellspacing='0' width='100%'><tbody><tr><td><div style='font-family: arial; font-weight: bold; font-size: 18px;'><br> Site Features:</div><table class='panel' style='background-color:#3265a3; width: 181px; color: white; font-family: tahoma,verdana; font-size: 13px; cursor:pointer;' border='1' bordercolor='#029bf7' cellpadding='0' cellspacing='0'><tbody><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[0]'>&nbsp;&nbsp;Back Home</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[1]'>&nbsp;&nbsp;Website Index</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[2]'>&nbsp;&nbsp;USAMU Pistol Guide</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[9]'>&nbsp;&nbsp;Zen in the Art of Shooting</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[3]'>&nbsp;&nbsp;Bullseye-L Forum</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[4]'>&nbsp;&nbsp;Clubs and Teams</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[7]'>&nbsp;&nbsp;Other Disciplines</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[11]'>&nbsp;&nbsp;About this Site </td></tr></tbody></table><br><a href='" + ad2 + "'><img src='premium2.jpg?v=" + rand + "' width='182' height='168' border='0'></a><br><br><a href='" + ad3 + "'><img src='premium3.jpg?v=" + rand + "' width='182' height='168' border='0'></a></td></tr></tbody></table> <table border='0' cellspacing='0' width='100%'> <tr> <td background='fadebar.jpg'>&nbsp;<br> <br> <br> <br> <br> <br> <br> <br> <br> <br> <br> </td> </tr> </table> <p><input type='text' size='1' maxlength='1' name='dummy' style='background-color:#FFFFFF; font-size:2px; border:1px #FFFFFF solid; border-color:#FFFFFF solid;'> </p> </form> </td> </tr> <tr> <td colspan='2'>&nbsp;</td> </tr> <tr> <td><img src='spacer.gif' width='736' height='1'></td> <td><img src='spacer.gif' width='187' height='1'></td></tr></table>");
}
}

