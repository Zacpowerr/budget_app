var category_list = [];
function addCategory() {
    var category = {
        "category_id" : $("#category_id_modal").val(),
        "threshold" : $("#threshold_modal").val(),
        "used_amount" : $("#used_amount_modal").val(),
    }
    category_list.push(category);
    var prev = $("#category_list").val()
    category_list.forEach(element => {
        $("#category_list").val(prev+JSON.stringify(element)+ ' - ')
        
    });
}

function getCategoryList(){
    return category_list;
}