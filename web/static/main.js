function is_valid(field, value) {
    if (field == "login") return value.match('^[a-z]{3,12}$') && verify_login(value);
    if (field == "password") return value.match('.{8,}');
    if (field == "rpassword") return value.match('.{8,}');
    if (field == "firstname") return value.match('^[A-Z{ĄĆĘŁŃÓŚŹŻ}][a-z{ąćęłńóśźż}]+$');
    if (field == "lastname") return value.match('^[A-Z{ĄĆĘŁŃÓŚŹŻ}][a-z{ąćęłńóśźż}]+$');
    if (field == "sex") return ['M', 'F'].includes(value);
    if (field == "photo") return value.match('^.*(\.png|\.jpg)$');
    return false;
}

function verify_login(value) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "https://infinite-hamlet-29399.herokuapp.com/check/" + value, true);
    xhr.onload = function (e) {
        if (xhr.readyState === 4) {
            var login = document.getElementById("login");
            var submit = document.getElementsByClassName("input-submit")[0]
            if (xhr.status === 200) {
                if (JSON.parse(xhr.response)[value] === "taken" && login.value === value) {
                    login.classList.add('is-invalid');
                    submit.disabled = true;
                }
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.send();
    return true;
}

function verify_passwords() {
    var pass = document.getElementById("password");
    var rpass = document.getElementById("rpassword");
    var pass_ok = (pass.value == rpass.value)
    if (pass_ok) {
        rpass.classList.remove('is-invalid');
    } else {
        rpass.classList.add('is-invalid');
    }
    return pass_ok;
}

function is_form_ready(inputs_array) {
    var all_valid = true;
    inputs_array.forEach(input => {
        if (!is_valid(input.id, input.value)) all_valid = false;
    })
    var pass_ok = verify_passwords()
    return all_valid && pass_ok;
}

function attach_events() {
    var submit = document.getElementsByClassName("input-submit")[0];
    submit.disabled = true;

    var inputs = document.getElementsByClassName("validated-input");
    var inputs_array = Array.prototype.slice.call(inputs)
    inputs_array.forEach(input => {
        input.addEventListener("input", e => {
            if (is_valid(e.target.id, e.target.value)) {
                e.target.classList.remove('is-invalid');
            } else {
                e.target.classList.add('is-invalid');
            }
            if (is_form_ready(inputs_array)){
                submit.disabled = false;
            } else {
                submit.disabled = true;
            }
        })
    });
}

//attach_events()