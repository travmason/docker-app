function goBack() {
    window.history.back();
}

function loading(){
    $("#loading").show();
    $("#content").hide();
}

function storeUploadData(name,sessions){
    sessionStorage.patient_name = name;
    sessionStorage.session_number = parseInt(sessions) + 1;
}

function clearSS(){
    sessionStorage.clear();
}

function alert(){
    alert("Hello");
}

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.collapsible');
    var instances = M.Collapsible.init(elems);

});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems);
});