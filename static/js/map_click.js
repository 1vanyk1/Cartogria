function mouse_up(status, cord_x, cord_y, zoom, user_id, points, e){
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
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            if (this.response['res']) {
                document.location.reload(true);
            }
        }
    };
    if (status == 1) {
        if (event.which == 1) {
            request.open("POST", "/api/move_point/" + clickX + "/" + clickY + "/" + cord_x + "/" + cord_y + "/" + zoom + "/" + user_id + "/" + points, true);
            request.send();
        }
    }
    return false;
}


function end_adding_shape(added, user_id) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/end_adding_shape/" + added + "/" + user_id, true);
    request.send();
    return false;
}


function change_status(status, user_id) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/change_status/" + status + "/" + user_id, true);
    request.send();
    return false;
}


function remove_last_point(user_id, e) {
    if (event.which == 3) {
        var request = new XMLHttpRequest();
        request.responseType = 'json'
        request.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.location.reload(true);
            }
        };
        request.open("POST", "/api/remove_last_point/" + user_id, true);
        request.send();
    }
    return false;
}


function remove_shape(elem_selected, e) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/remove_shape/" + elem_selected, true);
    request.send();
    return false;
}


function remove_mark(elem_selected, user_id, e) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/remove_mark/" + elem_selected + "/" + user_id, true);
    request.send();
    return false;
}


function add_frame(elem_selected, user_id, e) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/add_frame/" + elem_selected + "/" + user_id, true);
    request.send();
    return false;
}


function change_color(color, value, elem_id, e) {
    var request = new XMLHttpRequest();
    request.responseType = 'json'
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/change_color/" + color + "/" + value + "/" + elem_id, true);
    request.send();
    return false;
}


function click_on_point(status, cord_x, cord_y, zoom, user_id, elem_selected, p, e){
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
    if (status == 1) {
        if (event.which == 1) {
            var request = new XMLHttpRequest();
            request.open("POST", "/api/set_moving_point/" + elem_selected + "/" + p + "/" + user_id, true);
        } else if (event.which == 3) {
            var request = new XMLHttpRequest();
            request.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.location.reload(true);
                }
            };
            request.open("POST", "/api/delete_point/" + elem_selected + "/" + p + "/" + user_id, true);
        }
        request.send();
    }
    return false;
}


function click_on_mark(user_id, elem_id, e){
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.location.reload(true);
        }
    };
    request.open("POST", "/api/click_on_mark/" + elem_id + "/" + user_id, true);
    request.send();
    return false;
}


function add_moving_point(status, x_p, y_p, user_id, elem_selected, p, e){
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
    if (status == 1) {
        if (event.which == 1) {
            var request = new XMLHttpRequest();
            request.open("POST", "/api/add_moving_point/" + elem_selected + "/" + p + "/" + user_id + "/" + x_p + "/" + y_p, true);
        }
        request.send();
    }
    return false;
}


function click_on_item(status, cord_x, cord_y, zoom, user_id, elem_id, elem_selected, points, e){
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
    if (status == 2) {
        if (event.which == 1) {
            var request = new XMLHttpRequest();
            request.responseType = 'json'
            request.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.location.reload(true);
                }
            };
            request.open("POST", "/api/add_new_point/" + clickX + "/" + clickY + "/" + cord_x + "/" + cord_y + "/" + zoom + "/" + user_id + "/" + points, true);
            request.send();
        }
    } else if (status == 3) {
        if (event.which == 1) {
            var request = new XMLHttpRequest();
            request.responseType = 'json'
            request.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.location.reload(true);
                }
            };
            request.open("POST", "/api/add_new_mark/" + clickX + "/" + clickY + "/" + cord_x + "/" + cord_y + "/" + zoom + "/" + user_id, true);
            request.send();
        }
    } else if (event.which == 1) {
        if (elem_id == -1) {
            var request = new XMLHttpRequest();
            request.responseType = 'json'
            request.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.location.reload(true);
                }
            };
            request.open("POST", "/api/remove_moving_point/" + user_id, true);
            request.send();
            return false;
        } else {
            var request = new XMLHttpRequest();
            request.responseType = 'json'
            request.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    document.location.reload(true);
                }
            };
            request.open("POST", "/api/select_item/" + elem_id + "/" + user_id, true);
            request.send();
            return false;
        }
    }
    return false;
}