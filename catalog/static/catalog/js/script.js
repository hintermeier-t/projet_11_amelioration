var modification = false;

function save(clicked, url){
  //Function that call 'save' view
  $.ajax({
    type: "GET",
    url: url,
    data: {
        "product": clicked,
    },
    dataType: "json",
    success: function (data) {
        // any process in data
        alert("Produit sauvegardé")
    },
    failure: function () {
        alert("Impossible");
    }
});
var el = document.getElementById(String(clicked));
el.style.backgroundColor = "darkgrey"
el.disabled = true;

}

function mailModifier(url){
  if (modification == false){
    var p = document.getElementById("modifier");
    var modificateur = document.createRange().createContextualFragment('<input id="mail" type="text" placeholder="Entrez votre adresse mail"></input><button onclick="mailSave(\'../mail_save\')">Enregistrer</button>');
    p.append(modificateur);
    modification = true;
  }
  
}

function mailSave(url){
  var mail = document.getElementById('mail')
  $.ajax({
    type: "GET",
    url: url,
    data: {
        "email": mail.value,
    },
    dataType: "json",
    success: function (data) {
        // any process in data
        alert("Mail sauvegardé")
    },
    failure: function () {
        alert("Une erreur est survenue");
    }
});
}

function delete_fav(clicked, url){
  //Function that call 'delete' view
  $.ajax({
    type: "GET",
    url: url,
    data: {
        "product": clicked,
    },
    dataType: "json",
    success: function (data) {
        // any process in data
        alert("Produit retiré des favoris")
        window.location.reload()
    },
    failure: function () {
        alert("Impossible");
    }
});
var el = document.getElementById(String(clicked));
el.style.backgroundColor = "darkgrey"
el.disabled = true;

}