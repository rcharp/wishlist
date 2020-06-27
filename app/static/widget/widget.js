
(function(){
    var css = document.createElement('link');
    css.href = "embedjs.css";
    css.rel = "stylesheet";
    css.type = 'text/css';
    document.getElementsByTagName('head')[0].appendChild(css);

    $(document).ready(function() {
        $form = $("<form id='jsembed' action='/tokenize/' method='POST'></form>");
        $form.append("<label>Title</label>");
        $form.append("<br>")
        $form.append("<input type='text' class='title' name='title' value=''>");
        $form.append("<br>")
        $form.append("<label>Details</label>");
        $form.append("<br>")
        $form.append("<input type='text' class='details' name='details' value=''>");
        $form.append("<br>")
        $form.append("<button>Submit</button>");
        $(widget).html($form);


        $("#jsembed").submit(function(e) {
            e.preventDefault();
            var form = $(this);
            var serialized_form = form.serialize();
            serialized_form += "&username=" + localStorage.getItem("username");
            jwt_token = "";

            $.post({
                url: form.attr('action'),
                data: serialized_form
            })
            .always(function(data) {
                // Data was successfully encoded with JWT
                if(data.status == 200){
                    jwt_token = data.responseText;
                    $.post({
                        url: "/submit/",
                        data: "token=" + jwt_token
                    });
                } else {
                    // Failure behavior
                }
            });


        });
    });
});