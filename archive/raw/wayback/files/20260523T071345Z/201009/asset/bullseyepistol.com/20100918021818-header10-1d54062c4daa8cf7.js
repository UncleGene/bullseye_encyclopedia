var hand = "hand"; 
var color1 = "#BB7B04";
var color2 = "#914800";

var Nam = new Object();
Nam[1] = " 1. NRA Competition";
Nam[2] = " 2. Eligibility of Competitors";
Nam[3] = " 3. Equipment And Ammo";
Nam[4] = " 4. Official Targets";
Nam[5] = " 5. Shooting Positions";
Nam[6] = " 6. Range Standards";
Nam[7] = " 7. Courses Of Fire";
Nam[8] = " 8. Time Limits";
Nam[9] = " 9. Tournament Conditions";
Nam[10] = "10. Range Commands";
Nam[11] = "14. Scoring And Marking";
Nam[12] = "15. Decision Of Ties";
Nam[13] = "16. Challenges/Protests";
Nam[14] = "17. National Records";
Nam[15] = "18. Competitor's Duties";
Nam[16] = "19. National Classification";

var loc = new Object();
loc[1] = "rulebook1.htm";
loc[2] = "rulebook2.htm";
loc[3] = "rulebook3.htm";
loc[4] = "rulebook4.htm";
loc[5] = "rulebook5.htm";
loc[6] = "rulebook6.htm";
loc[7] = "rulebook7.htm";
loc[8] = "rulebook8.htm";
loc[9] = "rulebook9.htm";
loc[10] = "rulebook10.htm";
loc[11] = "rulebook14.htm";
loc[12] = "rulebook15.htm";
loc[13] = "rulebook16.htm";
loc[14] = "rulebook17.htm";
loc[15] = "rulebook18.htm";
loc[16] = "rulebook19.htm";

function footer()  {
if (self.window.name != "Print")  {
document.write("</td><td valign='top'><form action='NOACTION'><table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#EBD178'><tr><td><font size='3' face='Arial' color='#000000'><strong>NRA Pistol Rulebook:</strong></font>");
if (document.getElementById) {
document.write("<table border='1' cellpadding='0' cellspacing='0' width='181' bgcolor='#BB7B04' bordercolor='#808080' bordercolordark='#EBD178' bordercolorlight='#9F5000'>");
for (var x = 1; x <= 16; x++) {
document.write("<tr> <td onmouseover='this.style.backgroundColor=color2; this.style.cursor=hand;' onclick='location.href=loc[" + x + "]' onmouseout='this.style.backgroundColor=color1; this.style.cursor=hand;'><font color='#FFFFFF' size='2' face='Tahoma'>&nbsp;" + Nam[x] + "</font></td> </tr>");
}
document.write("</table>");
}
else {
document.write("<table border='0' cellpadding='0' cellspacing='0' width='181' bgcolor='#BB7B04' bordercolor='#808080' bordercolordark='#EBD178' bordercolorlight='#9F5000'>");
for (var x = 1; x <= 16; x++) {
document.write("<tr> <td><font color='#FFFFFF' size='2' face='Tahoma'>&nbsp;</font><a href='" + loc[x] + "'><font color='#FFFFFF' size='2' face='Tahoma'>" + Nam[x] + "</font></a></td> </tr>");
}
document.write("</table>");
}

document.write("</td></tr></table><table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#EBD178'><tr><td><font size='3' face='Arial' color='#000000'><strong>Search This Site:</strong></font><font size='2' face='Tahoma'><strong><br></strong></font><input type='text' size='13' maxlength='18' name='findit'><input type='button' value='Find' onclick='Search(this.form)'><br><font size='1' face='Tahoma' color='#000000'>(One Word Only)<br><br></font><font size='3' face='Arial' color='#000000'><strong>Site Quickstart:</strong></font><font size='1'><br></font><select name='jumper' size='1' onchange='changePage(this.form)'><option selected value>Select Topic</option><option value='alphadex.htm'>Site Index</option><option value='amucover.htm'>AMU Manual</option><option value='rulebook.htm'>NRA Rule Book</option><option value='links.htm#clubs'>Clubs/Teams</option><option value='links.htm#products'>Product Sources</option><option value='http://www.lava.net/~perrone/bullseye/'>Bullseye-L Forum</option><option value='why.htm'>About This Site</option><option value='other.htm'>Other Disciplines</option><option value='index.htm'>Back Home</option></select><input type='button' value='Go' onclick='changePage(this.form)'><p>&nbsp;</p><p>&nbsp;</p></td></tr></table><table border='0' cellspacing='0' width='100%'><tr><td background='fadebar3.gif'>&nbsp;<br><br><br><br><br><br><br><br><br><br></td></tr></table><p><input type='text' size='1' maxlength='1' name='dummy'></p></form></td></tr><tr><td colspan='2'>&nbsp;</td></tr><tr><td><img src='spacer.gif' width='560' height='1'></td><td><img src='spacer.gif' width='185' height='1'></td></tr></table>");
}
}
