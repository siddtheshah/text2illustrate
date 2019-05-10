$(function () {
    $('#preview_button').click(function(){
      console.log("Click registered");
      console.log($('form').serialize());
      $.ajax({
        type: "POST",
        url: 'http://localhost:8000/api/highlight_input',
        data: $('form').serialize(),
         success: function(result){
        console.log("Query returned");
        errorStr = "Error ";
        errorExist = false;
        for (i = 0; i < result.length; i++) {
          if (result[i][0] == "red") {
            errorStr = errorStr.concat(result[i][1]).concat(" ");
            errorExist = true;
          }
        }
        if (errorExist) {
          $('#preview_result').text(errorStr);
        } else {
          $('#preview_result').text("");
        }
      }});
    });
});