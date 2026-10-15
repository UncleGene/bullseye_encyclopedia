window.onError=null;

function mOver(p) {
p.style.backgroundColor='#0000a0';
p.style.cursor='hand';
}
function mOut(p) {
p.style.backgroundColor='#0181CD';
p.style.cursor='hand';
}
function Search(field) {
var str = field.findit.value;
var when = new Date();
when.setMonth(when.getMonth() + 1);
var date = when.toGMTString();
document.cookie = "search=" + str + "; expires=" + date + ";path=/";
window.location.href ="../../pages/search/index.html"
}
function showtime() {
var now=new Date();
var then = new Date("July 9, 2010 07:00:00")
var gap = then.getTime() - now.getTime();
gap = Math.floor(gap / (1000*60*60*24));
document.write("There are "+ (gap) +" days<br>until Camp Perry 2010!");
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
function eMail() {
var pb="bullseyepistol.com";
var pa="mail";
var pc=pa + "@" + pb;
document.write("<a href='mailto:" + pc + "'><font color='#FFFFFF' size='2' face='Tahoma'><strong>Feedback</strong></font></a>");
}
function changePage(form) {
if (form.jumper.selectedIndex == 0)
return;
else
window.location.href = form.jumper.options[form.jumper.selectedIndex].value;
}

function qut() {
var pd = new Date();
var pk = pd.getDate();
var a = (qt[pk] + "<br>" + atr[pk]);
document.write (a);
}

var qt = new Object()
qt[1] = "By working hard and using my mind, I could overcome my weakness to the point where I could be one of the best. "
qt[2] = "Any job worth doing is worth doing poorly! Get involved, now. And learn from your mistakes again and again until you are able to do it perfectly!"
qt[3] = "I firmly believe that any man's finest hour, the greatest fulfillment of all that he holds dear, is the moment when he has worked his heart out in a good cause and lies exhausted on the field of battle - victorious."
qt[4] = "Lack of something to feel important about is almost the greatest tragedy a person may have"
qt[5] = "Taking all of this information into account is no substitute for the experience of shooting real matches. For me, concentrating on my routine keeps me from thinking about anything else."
qt[6] = "There are four phases in the development of a shooter to be a champion: exploring, questioning, organizing, and accomplishing his goals."
qt[7] = "Do not be afraid of defeat.  You are never so near to victory as when defeated in a good cause."
qt[8] = "It's easy to have faith in yourself and have discipline when you're a winner, when you're number one. What you've got to have is faith and discipline when you're not yet a winner. "
qt[9] = "The spirit, the will to win and the will to excel - these are the things that endure and these are the qualities that are so much more important than any of the events that occasion them."
qt[10] = "A man can be as great as he wants to be. If you believe in yourself and have the courage, the determination, the dedication, the competitive drive and if you are willing to sacrifice the little things in life... it can be done."
qt[11] = "Anyone can succeed at almost anything for which he has unlimited enthusiasm."
qt[12] = "If you'll not settle for anything less than your best, you will be amazed at what you can accomplish in your lives."
qt[13] = "None of us will ever accomplish anything excellent or commanding except when he listens to this whisper which is heard by him alone."
qt[14] = "The harder you work, the harder it is to surrender. Once you learn to quit, it becomes a habit."
qt[15] = "Winning can be defined as the science of being totally prepared"
qt[16] = "I often heard ...'It's rapid fire that divides the men from the boys.' It is not the rapid fire itself that makes the division, but rather a lack of belief in oneself that he is capable."
qt[17] = "Don't be afraid of failure. See it as a learning experience that provides an opportunity for new growth."
qt[18] = "It is no use in saying we are doing our best. We have got to be successful in doing what is necessary."
qt[19] = "Once you get yourself in a certain frame of mind, what is the physical?"
qt[20] = "The only place where SUCCESS comes before WORK is in the dictionary"
qt[21] = "Winning is not a sometime thing; it's an all the time thing. You don't win once in a while; you don't do things right once in a while; you do them right all the time. Winning is a habit. Unfortunately, so is losing."
qt[22] = "Always behave like a duck. Appear calm and unruffled on the surface, but paddle like crazy underneath"
qt[23] = "Forget your competition; play the game to the best of your ability and the other guy will eventually screw up."
qt[24] = "Success is like anything worthwhile. It has a price. You have to pay the price to win and you have to pay the price to get to the point where success is possible. Most important, you must pay the price to stay there."
qt[25] = "Winning isn't everything; but wanting to win surely is."
qt[26] = "Your vision will become clear only when you can look into your own heart.  (Those) who look outside dream; (those) who look inside awake."
qt[27] = "The greatest pleasure in life is doing what people say you cannot do."
qt[28] = "You are the only shooter on the range. Don't concern yourself with the problems of other shooters."
qt[29] = "Ninety percent of this game is half mental."
qt[30] = "The significance of a man is not in what he attains but rather in what he longs to attain."
qt[31] = "The world belongs to the enthusiast who keeps his cool."

var atr = new Object()
atr[1] = "- Bart Starr"
atr[2] = "- Zig Ziglar"
atr[3] = "- Vince Lombardi"
atr[4] = "- Arthur E. Morgan"
atr[5] = "- Allen Fulford"
atr[6] = "- Oscar Weinmeister"
atr[7] = "- Henry Ward Beecher"
atr[8] = "- Vince Lombardi"
atr[9] = "- Vince Lombardi"
atr[10] = "- Vince Lombardi"
atr[11] = "- Charles Schwab"
atr[12] = "- Vince Lombardi"
atr[13] = "- Ralph Waldo Emerson"
atr[14] = "- Vince Lombardi"
atr[15] = "- George Allen"
atr[16] = "- David Cartes"
atr[17] = "- Hideharu Onuma "
atr[18] = "- Winston Churchill"
atr[19] = "- Wynton Marsalis"
atr[20] = "- Vidal Sassoon"
atr[21] = "- Vince Lombardi"
atr[22] = "- Anon."
atr[23] = "- John Dreyer (originally explaining golf)"
atr[24] = "- Vince Lombardi"
atr[25] = "- Vince Lombardi"
atr[26] = "- Carl Jung"
atr[27] = "- Walter Bagehot"
atr[28] = "- Frank Higginson"
atr[29] = "- Yogi Berra"
atr[30] = "- Kahlil Gibran"
atr[31] = "- William McFee"