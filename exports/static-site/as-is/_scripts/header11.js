window.onError=null;

function mOver(p) {
p.style.backgroundColor='#072f61';
}
function mOut(p) {
p.style.backgroundColor='#3265a3';
}
function Search(field) {
var str = field.findit.value;
var when = new Date();
when.setMonth(when.getMonth() + 1);
var date = when.toGMTString();
document.cookie = "search=" + str + "; expires=" + date + ";path=/";
window.location.href ="pages/search/index.html"
}
function showtime() {
var now=new Date();
var then = new Date("July 11, 2015 01:00:00")
var gap = then.getTime() - now.getTime();
gap = Math.abs(Math.floor(gap / (1000*60*60*24)));
hundi = Math.floor(gap / 100)
deci = Math.floor((gap - (hundi * 100)) / 10)
digi = Math.floor((gap - (hundi * 100) - (deci * 10)))
document.write("<img src=" + hundi + ".gif height=50 width=25><img src=" + deci + ".gif height=50 width=25><img src=" + digi + ".gif height=50 width=25>");
}
function mapQuest(field) {
var start = field.start.value;
var end = field.end.value;
var travel = "http://www.mapquest.com/directions/main.adp?go=1&do=nw&ct=NA&1y=US&1a=&1p=&1c=&1s=&1z=" + start + "&1ah=&2y=US&2a=&2p=&2c=&2s=&2z=" + end + "&2ah=&lr=2&x=74&y=11"
top.location.href = travel
}
function weatherUnderground(field) {
var place = field.zipcode.value;
var gothere = "http://www.weatherunderground.com/cgi-bin/findweather/getForecast?query=" + (place)
top.location.href = gothere
}

function rangeSearch(field) {
var start = field.zipcode.value;
var radius = field.distance.value;
var gothere = "http://www.shootingplaces.com/?radius=" + (radius) + "&origin_point=" + (start)
top.location.href = gothere
}

function nraLook(field) {
var code = field.MemID.value;
document.nraLookup.MemberID.value = code;
document.nraLookup.submit()
}

function eMail() {
var pb="bullseyepistol.com";
var pa="mail";
var pc=pa + "@" + pb;
document.write("<a href='mailto:" + pc + "'><strong>Feedback</strong></a>");
}
function changePage(form) {
if (form.jumper.selectedIndex == 0)
return;
else
window.location.href = form.jumper.options[form.jumper.selectedIndex].value;
}

function copyYear() {
var cy=new Date();
document.write(cy.getFullYear());
}
function block(title) {
document.write ("<table style='width: 100%;' border='0' cellpadding='0' cellspacing='0'><tbody><tr><td class='navb' style='width: 238px;'>" + title + "</td><td style='width: 22px;background-color:#103d16;'><img alt='' src='shared/images/roundbar6.jpg' style='border: 0px solid; width:22px; height:26px; vertical-align: top;' hspace='0' vspace='0'></td></tr>");
}
function qut() {
var pd = new Date();
var pm = pd.getMonth() + 1; 
var pk = pd.getDate();
var am = Math.floor(pm / 2); if ((pm / 2) == am) { pk = pk + 31 };
var a = (qt[pk] + "<br><i>" + atr[pk] + "</i>");
document.write (a);
}

function bac() {
imageNo--;
if (imageNo < 1) {imageNo = 15}
pix.innerHTML = (ph[imageNo] + "<img style='width: 190px; height: 185px; border: 0px;' alt='' src='http://www.bullseyepistol.com/image" + imageNo + ".jpg'></a>");
}

function frw() {
imageNo++;
if (imageNo > 15) {imageNo = 1}
pix.innerHTML = (ph[imageNo] + "<img style='width: 190px; height: 185px; border: 0px;' alt='' src='http://www.bullseyepistol.com/image" + imageNo + ".jpg'></a>");
}

var ph = new Object()
ph[1] = "<a href='articles/perfecting-technique/a-fundamentals-clinic/index.html'>" 
ph[2] = "<a href='articles/perfecting-technique/focus-on-the-fundamentals/index.html'>" 
ph[3] = "<a href='articles/perfecting-technique/goal-setting-and-training/index.html'>" 
ph[4] = "<a href='articles/introductory-information/tips-for-bullseye-shooting/index.html'>" 
ph[5] = "<a href='http://www.bullseyepistol.com/'>"
ph[6] = "<a href='articles/perfecting-technique/three-lessons/index.html'>" 
ph[7] = "<a href='articles/tools-of-the-trade/the-custom-built-bullseye-gun/index.html'>" 
ph[8] = "<a href='articles/technical-information/vision-topics/index.html'>" 
ph[9] = "<a href='articles/shooting-psychology/achieving-the-zone-in-shooting/index.html'>" 
ph[10] = "<a href='articles/perfecting-technique/advanced-beginner-q-a/index.html'>" 
ph[11] = "<a href='articles/technical-information/maintaining-your-hammerli-208s/index.html'>"
ph[12] = "<a href='articles/technical-information/m-1911-pistol-lubrication/index.html'>" 
ph[13] = "<a href='articles/shooting-psychology/the-psychology-of-routine/index.html'>"
ph[14] = "<a href='articles/perfecting-technique/army-marksmanship-training-guide/index.html'>"
ph[15] = "<a href='articles/tools-of-the-trade/the-benefits-of-custom-anatomical-grips/index.html'>"

var qt = new Object()
qt[1] = "By working hard and using my mind, I could overcome my weakness to the point where I could be one of the best."
qt[2] = "A real decision is measured by the fact that you've taken a new action. If there's no action, you haven't truly decided."
qt[3] = "Any job worth doing is worth doing poorly! Get involved, now. And learn from your mistakes again and again until you are able to do it perfectly!"
qt[4] = "Adversity causes some men to break; others to break records."
qt[5] = "I firmly believe that any man's finest hour, the greatest fulfillment of all that he holds dear, is the moment when he has worked his heart out in a good cause and lies exhausted on the field of battle - victorious."
qt[6] = "Determine never to be idle. No person will have occasion to complain of the want of time who never loses any. It is wonderful how much may be done if we are always doing."
qt[7] = "Lack of something to feel important about is almost the greatest tragedy a person may have"
qt[8] = "I don't believe you have to be better than everybody else. I believe you have to be better than you ever thought you could be."
qt[9] = "Taking all of this information into account is no substitute for the experience of shooting real matches. For me, concentrating on my routine keeps me from thinking about anything else."
qt[10] = "I figure practice puts your brains in your muscles."
qt[11] = "There are four phases in the development of a shooter to be a champion: exploring, questioning, organizing, and accomplishing his goals."
qt[12] = "I hated every minute of training, but I said, Don't quit. Suffer now and live the rest of your life as a champion."
qt[13] = "Do not be afraid of defeat.  You are never so near to victory as when defeated in a good cause."
qt[14] = "If a tie is like kissing your sister, losing is like kissing your grandmother with her teeth out."
qt[15] = "It's easy to have faith in yourself and have discipline when you're a winner, when you're number one. What you've got to have is faith and discipline when you're not yet a winner."
qt[16] = "If you don't invest very much, then defeat doesn't hurt very much and winning is not very exciting."
qt[17] = "The spirit, the will to win and the will to excel - these are the things that endure and these are the qualities that are so much more important than any of the events that occasion them."
qt[18] = "If you don't love what you do, you won't do it with much conviction or passion."
qt[19] = "A man can be as great as he wants to be. If you believe in yourself and have the courage, the determination, the dedication, the competitive drive and if you are willing to sacrifice the little things in life... it can be done."
qt[20] = "In the end, the game comes down to one thing: man against man. May the best man win."
qt[21] = "Anyone can succeed at almost anything for which he has unlimited enthusiasm."
qt[22] = "In theory there is no difference between theory and practice. But in practice, there is."
qt[23] = "If you'll not settle for anything less than your best, you will be amazed at what you can accomplish in your lives."
qt[24] = "It's great to win, but it's also great fun to be in the thick of any truly well and hard fought contest against opponents you respect, whatever the outcome."
qt[25] = "None of us will ever accomplish anything excellent or commanding except when he listens to this whisper which is heard by him alone."
qt[26] = "It's lack of faith that makes people afraid of meeting challenges, and I believed in myself."
qt[27] = "The harder you work, the harder it is to surrender. Once you learn to quit, it becomes a habit."
qt[28] = "Most people give up just when they're about to achieve success. They quit on the one yard line. They give up at the last minute of the game, one foot from a winning touchdown."
qt[29] = "Winning can be defined as the science of being totally prepared"
qt[30] = "Only a man who knows what it is like to be defeated can reach down to the bottom of his soul and come up with the extra ounce of power it takes to win when the match is even."
qt[31] = "I often heard ... 'It's rapid fire that divides the men from the boys.' It is not the rapid fire itself that makes the division, but rather a lack of belief in oneself that he is capable."
qt[32] = "People often say that motivation doesn't last. Well, neither does bathing - that's why we recommend it daily."
qt[33] = "Don't be afraid of failure. See it as a learning experience that provides an opportunity for new growth."
qt[34] = "Some people say I have attitude - maybe I do, but I think you have to.  You have to believe in yourself when no one else does - that makes you a winner right there."
qt[35] = "It is no use in saying we are doing our best. We have got to be successful in doing what is necessary."
qt[36] = "Success in this game depends less on strength of body than strength of mind and character."
qt[37] = "Once you get yourself in a certain frame of mind, what is the physical?"
qt[38] = "Take your victories, whatever they may be, cherish them, use them, but don't settle for them."
qt[39] = "The only place where SUCCESS comes before WORK is in the dictionary"
qt[40] = "The difference between the impossible and the possible lies in a man's determination."
qt[41] = "Winning is not a sometime thing; it's an all the time thing. You don't win once in a while; you don't do things right once in a while; you do them right all the time. Winning is a habit. Unfortunately, so is losing."
qt[42] = "The more you sweat in practice, the less you bleed in battle."
qt[43] = "Always behave like a duck. Appear calm and unruffled on the surface, but paddle like crazy underneath"
qt[44] = "There are only two options regarding commitment; you're either in or you're out. There's no such thing as life in-between."
qt[45] = "Forget your competition; play the game to the best of your ability and the other guy will eventually screw up."
qt[46] = "Without self-discipline, success is impossible, period."
qt[47] = "Success is like anything worthwhile. It has a price. You have to pay the price to win and you have to pay the price to get to the point where success is possible. Most important, you must pay the price to stay there."
qt[48] = "You are never really playing an opponent. You are playing yourself, your own highest standards, and when you reach your limits, that is real joy."
qt[49] = "Winning isn't everything; but wanting to win surely is."
qt[50] = "You can't just beat [an opponent], you have to leave a lasting impression in their mind so they never want to see you again."
qt[51] = "Your vision will become clear only when you can look into your own heart.  [Those] who look outside dream; [those] who look inside awake."
qt[52] = "You find that you have peace of mind and can enjoy yourself, get more sleep, and rest when you know that it was a one hundred percent effort that you gave - win or lose."
qt[53] = "The greatest pleasure in life is doing what people say you cannot do."
qt[54] = "You owe it to yourself to be the best you can possible be - in [sport] and in life."
qt[55] = "You are the only shooter on the range. Don't concern yourself with the problems of other shooters."
qt[56] = "You were born to win, but to be a winner, you must plan to win, prepare to win, and expect to win."
qt[57] = "Ninety percent of this game is half mental."
qt[58] = "Champions are made from something they have deep inside them a desire, a dream, a vision. They have to have the skill and the will. But the will must be stronger than the skill."
qt[59] = "The significance of a man is not in what he attains but rather in what he longs to attain."
qt[60] = "The tragedy of life doesnt lie in not reaching your goal. The tragedy lies in having no goals to reach."
qt[61] = "The world belongs to the enthusiast who keeps his cool."
qt[62] = "In Illinois, our Governors always serve two terms: the first in office, and the second in prison."

var atr = new Object()
atr[1] = "- Bart Starr"
atr[2] = "- Tony Robbins"
atr[3] = "- Zig Ziglar"
atr[4] = "- William A. Ward "
atr[5] = "- Vince Lombardi"
atr[6] = "- Thomas Jefferson "
atr[7] = "- Arthur E. Morgan"
atr[8] = "- Ken Venturi "
atr[9] = "- Allen Fulford"
atr[10] = "- Sam Snead"
atr[11] = "- Oscar Weinmeister"
atr[12] = "- Muhammad Ali "
atr[13] = "- Henry Ward Beecher"
atr[14] = "- George Brett"
atr[15] = "- Vince Lombardi"
atr[16] = "- Dick Vermeil"
atr[17] = "- Vince Lombardi"
atr[18] = "- Mia Hamm "
atr[19] = "- Vince Lombardi"
atr[20] = "- Sam Huff"
atr[21] = "- Charles Schwab"
atr[22] = "- Yogi Berra"
atr[23] = "- Vince Lombardi"
atr[24] = "- Jack Nicklaus"
atr[25] = "- Ralph Waldo Emerson"
atr[26] = "- Muhammad Ali "
atr[27] = "- Vince Lombardi"
atr[28] = "- Ross Perot"
atr[29] = "- George Allen"
atr[30] = "- Muhammad Ali "
atr[31] = "- David Cartes"
atr[32] = "- Zig Ziglar "
atr[33] = "- Hideharu Onuma "
atr[34] = "- Venus Williams"
atr[35] = "- Winston Churchill"
atr[36] = "- Arnold Palmer"
atr[37] = "- Wynton Marsalis"
atr[38] = "- Mia Hamm "
atr[39] = "- Vidal Sassoon"
atr[40] = "- Tommy Lasorda"
atr[41] = "- Vince Lombardi"
atr[42] = "- Author Unknown"
atr[43] = "- Anon."
atr[44] = "- Pat Riley "
atr[45] = "- John Dreyer"
atr[46] = "- Lou Holtz"
atr[47] = "- Vince Lombardi"
atr[48] = "- Arthur Ashe"
atr[49] = "- Vince Lombardi"
atr[50] = "- Mia Hamm "
atr[51] = "- Carl Jung"
atr[52] = "- Gordie Howe"
atr[53] = "- Walter Bagehot"
atr[54] = "- Pete Rose"
atr[55] = "- Frank Higginson"
atr[56] = "- Zig Ziglar "
atr[57] = "- Yogi Berra"
atr[58] = "- Muhammad Ali"
atr[59] = "- Kahlil Gibran"
atr[60] = "- Benjamin Mays"
atr[61] = "- William McFee"
atr[62] = "- Resident of the Land of Lincoln"

imageNo = 1;  