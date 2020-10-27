function attach_events() {
    var firstname = document.getElementById("firstname");
    firstname.addEventListener("change", function(e) {
        alert("test")
    })
}

attach_events()