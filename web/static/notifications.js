template = `<div id="TOAST_ID" class="toast" data-autohide="false" role="alert" aria-live="assertive" aria-atomic="true">
  <div class="toast-header">
    <strong class="mr-auto">TOAST_TITLE</strong>
    <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
      <span aria-hidden="true">&times;</span>
    </button>
  </div>
  <div class="toast-body">TOAST_BODY</div>
 </div>`

function appendHtml(el, str) {
    var div = document.createElement('div');
    div.innerHTML = str;
    while (div.children.length > 0) {
        el.appendChild(div.children[0]);
    }
}

function uuid4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function check_notifications() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var notifications = JSON.parse(xhr.responseText);
            div = document.getElementById('toasts');
            for (i=0; i<notifications.length; i++){
                new_toast = template.replace("TOAST_BODY", notifications[i]["text"]);
                new_toast = new_toast.replace("TOAST_TITLE", notifications[i]["time"]);
                new_toast = new_toast.replace("TOAST_ID", notifications[i]["uuid"]);
                appendHtml(div, new_toast);
                $("#" + notifications[i]["uuid"]).toast('show');
            }
        }
    }
    xhr.open("POST", "/notifications", true);
    xhr.send();
    setTimeout(check_notifications, 5000)
}

$(document).ready(function(){
    check_notifications();
});
