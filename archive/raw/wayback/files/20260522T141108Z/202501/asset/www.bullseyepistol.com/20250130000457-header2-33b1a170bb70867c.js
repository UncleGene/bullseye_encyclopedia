var hand = "hand"  
var color1 = "#009030"
var color2 = "#006C00"
var loc = new Object()
loc[0] = "chapterf.htm"
loc[1] = "chapter0.htm"
loc[2] = "chapter1.htm"
loc[3] = "chapter2.htm"
loc[4] = "chapter3.htm"
loc[5] = "chapter4.htm"
loc[6] = "chapter5.htm"
loc[7] = "chapter6.htm"
loc[8] = "chapter7.htm"
loc[9] = "chapter8.htm"
loc[10] = "chapter9.htm"
loc[11] = "chapter10.htm"
loc[12] = "annex2.htm"
loc[13] = "glossary.htm"

function footer()  {
if (self.window.name != "Print")  {
document.write("</td><td valign='top'><form action='NOACTION'><table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#EBD178'><tr><td><div style='font-family: arial; font-weight: bold; font-size: 18px;'>AMU Pistol Guide:</div>");

document.write("<table class='panel' style='color: white; cursor:pointer; font-family: tahoma; font-size:13px;' border='1' bgcolor='#009030' bordercolor='#000000' cellpadding='0' cellspacing='0' width='181'> <tbody> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[0]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;Foreword</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[1]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;Introduction: Elements</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[2]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;1 Minimum Arc of Movement</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[3]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;2 Sight Alignment</td> </tr> <tr> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[4]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;3 Trigger Control</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[5]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;4 Establish a System</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[6]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;5 Slow Fire</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[7]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;6 Sustained Fire</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[8]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;7 Mental Discipline</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[9]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;8 Physical Conditioning</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[10]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;&nbsp;9 Diet and Health</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[11]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;10 Alcohol, Tobacco, Coffee</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[12]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;Annex: Properties of the Eye</td> </tr> <tr> <td onmouseover='this.style.backgroundColor=color2;' onclick='location.href=loc[13]' onmouseout='this.style.backgroundColor=color1;'>&nbsp;Glossary of Terms Used</td> </tr> </tbody> </table>");

document.write("<br></td></tr></table><table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#EBD178'><tr><td><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Search This Site:</div><input type='text' size='13' maxlength='18' name='findit'><input type='button' value='Find' onclick='Search(this.form)'><div style='font-family: arial; font-size: 11px;'>(One word works best)<br> <br> </div><div style='font-family: arial; font-weight: bold; font-size: 18px;'>Site Quickstart:</div><select name='jumper' size='1' onchange='changePage(this.form)'><option selected value>Select Topic</option><option value='alphadex.htm'>Site Index</option><option value='amucover.htm'>AMU Manual</option><option value='http://www.nrahq.org/compete/RuleBooks/Pistol/pst-index.pdf'>NRA Rule Book</option><option value='links.htm#clubs'>Clubs/Teams</option><option value='links.htm#products'>Product Sources</option><option value='http://bullseyepistol.forumotion.com/'>Bullseye-L Forum</option><option value='why.htm'>About This Site</option><option value='other.htm'>Other Disciplines</option><option value='index.htm'>Back Home</option></select><input type='button' value='Go' onclick='changePage(this.form)'><p>&nbsp;</p><p>&nbsp;</p></td></tr></table><table border='0' cellspacing='0' width='100%'><tr><td background='fadebar3.jpg'>&nbsp;<br><br><br><br><br><br><br><br><br><br></td></tr></table><p><input type='text' size='1' maxlength='1' name='dummy' style='background-color:#FFFFFF; font-size:2px; border:1px #FFFFFF solid; border-color:#FFFFFF solid;'></p></form></td></tr><tr><td colspan='2'>&nbsp;</td></tr><tr><td><img src='spacer.gif' width='736' height='1'></td><td><img src='spacer.gif' width='185' height='1'></td></tr></table>")
}
}
