$(".submit-form").click(function () {
    console.log($(this).parents(".modal"))
    $(this).parents(".modal").find('form').submit();
});

$("#delete-note-modal").on("show.bs.modal", function(event) {
   var button = $(event.relatedTarget);
   $("#delete-note-modal input[name=pk]").val(button.data("note-pk"));
   $(this).find("div.modal-body").text(
       button.prevAll(".note-content").text()
   )
});

$("#edit-note-modal").on("show.bs.modal", function(event) {
   var button = $(event.relatedTarget);
   var pk = button.data("note-pk");
   var url = button.data("form-get-url");
   $.ajax({
       url: url,
       data: {pk: pk},
       type: 'get',
       beforeSend: function () {
           $("#edit-note-modal").find(".modal-body").html(
               '<div class="loader">Loading...</div>'
           );
           return true;
       },
       success: function (data, textStatus, jqXHR) {
           $("#edit-note-modal").find(".modal-body").html(data);
       }
   })
});