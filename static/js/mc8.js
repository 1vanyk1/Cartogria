//function openNewBackgroundTab(){
//    var a = document.createElement("a");
//    a.href = "http://www.google.com/";
//    var evt = document.createEvent("MouseEvents");
//    evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0,
//                                true, false, false, false, 0, null);
//    a.dispatchEvent(evt);
//}
let parent = document.getElementById('delta');
parent.onmouseover = parent.onmouseout = parent.onmousemove = handleEvent;

function UserAction(x, y) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             alert(this.responseText);
         }
    };
    request.open("POST", "http://localhost:5000/api/get_click_pos/" + x + "/" + y, true);
    request.send();
}

function handleEvent(e){
    var evt = e ? e:window.event;
    var clickX=0, clickY=0;
    if ((evt.clientX || evt.clientY) && document.body && document.body.scrollLeft!=null) {
        clickX = evt.clientX + document.body.scrollLeft;
        clickY = evt.clientY + document.body.scrollTop;
    }
    if ((evt.clientX || evt.clientY) && document.compatMode=='CSS1Compat' && document.documentElement && document.documentElement.scrollLeft!=null) {
        clickX = evt.clientX + document.documentElement.scrollLeft;
        clickY = evt.clientY + document.documentElement.scrollTop;
    }
    if (evt.pageX || evt.pageY) {
        clickX = evt.pageX;
        clickY = evt.pageY;
    }
    UserAction(clickX, clickY);
    return false;
}