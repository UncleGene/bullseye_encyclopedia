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
loc[1] = "index.html";
loc[2] = "../2-eligibility-of-competitors/index.html";
loc[3] = "../3-equipment-and-ammunition/index.html";
loc[4] = "../4-targets/index.html";
loc[5] = "../5-positions/index.html";
loc[6] = "../6-range-standards/index.html";
loc[7] = "../7-courses-of-fire/index.html";
loc[8] = "../8-time-limits/index.html";
loc[9] = "../9-tournament-conditions/index.html";
loc[10] = "../10-range-commands-and-operations/index.html";
loc[11] = "../14-scoring-and-marking/index.html";
loc[12] = "../15-decision-of-ties/index.html";
loc[13] = "../16-challenges-and-protests/index.html";
loc[14] = "../17-national-records/index.html";
loc[15] = "../18-competitor-s-responsibilities/index.html";
loc[16] = "../19-national-pistol-classification/index.html";

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

document.write("</td></tr></table><table border='0' cellpadding='2' cellspacing='0' width='100%' bgcolor='#EBD178'><tr><td><font size='3' face='Arial' color='#000000'><strong>Search This Site:</strong></font><font size='2' face='Tahoma'><strong><br></strong></font><input type='text' size='13' maxlength='18' name='findit'><input type='button' value='Find' onclick='Search(this.form)'><br><font size='1' face='Tahoma' color='#000000'>(One Word Only)<br><br></font><font size='3' face='Arial' color='#000000'><strong>Site Quickstart:</strong></font><font size='1'><br></font><select name='jumper' size='1' onchange='changePage(this.form)'><option selected value>Select Topic</option><option value='../../site-reference-general-index/website-topic-index/index.html'>Site Index</option><option value='../../perfecting-technique/army-marksmanship-training-guide/index.html'>AMU Manual</option><option value='../conventional-pistol-rules/index.html'>NRA Rule Book</option><option value='../../site-reference-general-index/links-to-other-sites/index.html#clubs'>Clubs/Teams</option><option value='../../site-reference-general-index/links-to-other-sites/index.html#products'>Product Sources</option><option value='http://www.lava.net/~perrone/bullseye/'>Bullseye-L Forum</option><option value='../../site-reference-general-index/about-this-website/index.html'>About This Site</option><option value='../../site-reference-general-index/other-popular-disciplines/index.html'>Other Disciplines</option><option value='../../../index.html'>Back Home</option></select><input type='button' value='Go' onclick='changePage(this.form)'><p>&nbsp;</p><p>&nbsp;</p></td></tr></table><table border='0' cellspacing='0' width='100%'><tr><td background='../../../shared/images/fadebar3.gif'>&nbsp;<br><br><br><br><br><br><br><br><br><br></td></tr></table><p><input type='text' size='1' maxlength='1' name='dummy'></p></form></td></tr><tr><td colspan='2'>&nbsp;</td></tr><tr><td><img src='../../../shared/images/spacer.gif' width='560' height='1'></td><td><img src='../../../shared/images/spacer.gif' width='185' height='1'></td></tr></table>");
}
}
