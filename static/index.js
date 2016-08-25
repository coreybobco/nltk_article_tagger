onload = function(){
    var button = document.querySelector("button");
    var show_output = function() { 
        active_output.value = this.responseText;
    }
    button.onclick = function() {
        //Grab the values of which tabs the generator will pull input from       
        var article = document.querySelector("#input").value

        var req = new XMLHttpRequest()
        req.addEventListener("load", show_output)
        req.open("post", "./tag", true)
        req.send(article)
    }
}