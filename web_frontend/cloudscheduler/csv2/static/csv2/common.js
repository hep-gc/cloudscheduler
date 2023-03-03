function show_group(group_name){
    if (group_name.length > 0) {
        document.location.hash = group_name;
    }
}


function search(id_tag) {
    // Declare variables
    var input, filter, ul, li, x, i;
    input = document.getElementById("search-" + id_tag)
    filter = input.value.toUpperCase();
    ul = document.getElementById("ul-" + id_tag);
    li = ul.getElementsByTagName('tr');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {

        x = li[i].getElementsByTagName('input')[0];
        if (x.type === "submit" || x.value.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
