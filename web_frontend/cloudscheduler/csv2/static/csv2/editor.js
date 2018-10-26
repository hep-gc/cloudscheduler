
function createEditor(name) {
    // find the textarea
    var textarea = document.querySelector("form textarea[id=" + name + "]");

    // create ace editor 
    var editor = ace.edit()
    editor.container.style.height = "70%"
    editor.container.style.width = "100%"
    editor.session.setValue(textarea.value)
    editor.setTheme("ace/theme/dracula");
    editor.getSession().setMode("ace/mode/yaml");


    // replace textarea with ace
    textarea.parentNode.insertBefore(editor.container, textarea)
    textarea.style.display = "none"
    // find the parent form and add submit event listener
    var form = textarea
    while (form && form.localName != "form") form = form.parentNode
    form.addEventListener("submit", function() {
        // update value of textarea to match value in ace
        textarea.value = editor.getValue()
    }, true)
}


setTimeout(function(){ 
  document.getElementById("message").innerHTML = "";
}, 5000);