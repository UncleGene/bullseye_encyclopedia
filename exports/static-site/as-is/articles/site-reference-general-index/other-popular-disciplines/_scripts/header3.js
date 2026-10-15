var rand = Math.floor(Math.random()*1001)
var ad2 = "../../../pages/redirect2/index.html?v=" + rand
var ad3 = "../../../pages/redirect3/index.html?v=" + rand

var color1 = "#3265a3"
var color2 = "#072f61"
var loc = new Object()
loc[0] = "../../../index.html"
loc[1] = "../website-topic-index/index.html"
loc[2] = "../../perfecting-technique/army-marksmanship-training-guide/index.html"
loc[3] = "https://www.bullseyeforum.net/"
loc[4] = "../links-to-other-sites/index.html#clubs"
loc[5] = "../links-to-other-sites/index.html#directory"
loc[6] = "../links-to-other-sites/index.html#products"
loc[7] = "index.html"
loc[9] = "../../zen-in-the-art-of-shooting/introduction-to-zen-in-shooting/index.html"
loc[10] = "../../the-reference-room/studio-recorded-audio-files-of-range-commands/index.html"
loc[11] = "../about-this-website/index.html"

function mOver(p) {
p.style.backgroundColor='#072f61';
}
function mOut(p) {
p.style.backgroundColor='#3265a3';
}

function footer()  {
if (self.window.name != "Print")  {
document.write("</td><td valign='top' align='center'><form onsubmit='Search(this); return false;'> <table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#8eb3d8'> <tr> <td><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Search This Site:</div><input type='text' size='13' maxlength='18' name='findit' onkeydown='if(event.keyCode===13){Search(this.form);return false;}'> <input type='button' value='Find' onclick='Search(this.form)'><br> <div style='font-family: arial; font-size: 11px;'>(One word works best)<br> <br> </div><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Site Quickstart:</div><select name='jumper' size='1' onchange='changePage(this.form)'> <option selected value>Select Topic</option> <option value='../website-topic-index/index.html'>Website Index</option> <option value='../../perfecting-technique/army-marksmanship-training-guide/index.html'>USAMU Manual</option> <option value='https://competitions.nra.org/competition-resources/rule-books/'>NRA Rule Book</option> <option value='../../zen-in-the-art-of-shooting/introduction-to-zen-in-shooting/index.html'>Zen in Shooting</option> <option value='../../the-reference-room/studio-recorded-audio-files-of-range-commands/index.html'>Range Commands</option> <option value='https://www.bullseyeforum.net/'>Bullseye-L Forum</option> <option value='../links-to-other-sites/index.html#clubs'>Clubs &amp; Teams</option> <option value='index.html'>Other Disciplines</option> <option value='../about-this-website/index.html'>About This Site</option> <option value='../../../index.html'>Back Home</option> </select><input type='button' value='Go' onclick='changePage(this.form)'></td></tr></table>");

document.write("<table bgcolor='#8eb3d8' border='0' cellpadding='2' cellspacing='0' width='100%'><tbody><tr><td><div style='font-family: arial; font-weight: bold; font-size: 18px;'><br> Site Features:</div><table class='panel' style='background-color:#3265a3; width: 181px; color: white; font-family: tahoma,verdana; font-size: 13px; cursor:pointer;' border='1' bordercolor='#029bf7' cellpadding='0' cellspacing='0'><tbody><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[0]'>&nbsp;&nbsp;Back Home</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[1]'>&nbsp;&nbsp;Website Index</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[2]'>&nbsp;&nbsp;USAMU Pistol Guide</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[9]'>&nbsp;&nbsp;Zen in the Art of Shooting</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[3]'>&nbsp;&nbsp;Bullseye-L Forum</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[4]'>&nbsp;&nbsp;Clubs and Teams</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[7]'>&nbsp;&nbsp;Other Disciplines</td></tr><tr><td onmouseover='mOver(this);' onmouseout='mOut(this);' onclick='location.href=loc[11]'>&nbsp;&nbsp;About this Site </td></tr></tbody></table><br><img src='../../../shared/images/premium2.jpg?v=" + rand + "' width='182' height='168' border='0'><br><br><img src='../../../shared/images/premium3.jpg?v=" + rand + "' width='182' height='168' border='0'></td></tr></tbody></table> <table border='0' cellspacing='0' width='100%'> <tr> <td background='../../../shared/images/fadebar.jpg'>&nbsp;<br> <br> <br> <br> <br> <br> <br> <br> <br> <br> <br> </td> </tr> </table> <p><input type='text' size='1' maxlength='1' name='dummy' style='background-color:#FFFFFF; font-size:2px; border:1px #FFFFFF solid; border-color:#FFFFFF solid;'> </p> </form> </td> </tr> <tr> <td colspan='2'>&nbsp;</td> </tr> <tr> <td><img src='../../../shared/images/spacer.gif' width='736' height='1'></td> <td><img src='../../../shared/images/spacer.gif' width='187' height='1'></td></tr></table>");
}
}

