onload = function(){
    var button = document.querySelector("button");
    var show_output = function() { 
        document.querySelector("#suggested_tags").value = this.responseText;
    }
    button.onclick = function() {
        //Grab the values of which tabs the generator will pull input from
        var data = {}
        data['title'] = document.querySelector("#article_title").value
        data['article'] = document.querySelector("#article").value
        data = JSON.stringify(data)
        var req = new XMLHttpRequest()
        // req.setRequestHeader("Content-type", "application/json");
        req.addEventListener("load", show_output)
        req.open("post", "./tag", true)
        req.send(data)
    }
}