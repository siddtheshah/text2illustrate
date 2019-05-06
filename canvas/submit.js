var titlesAndMotion;
$(function () {
    $('#submit_button').click(function(){
      console.log("Click registered");
      console.log($('form').serialize());
      $.ajax({
        type: "POST",
        url: 'http://localhost:5000/api/process_text',
        data: $('form').serialize(),
         success: function(result){
        console.log("Query returned");
        // $('output').text = result[0][0];
        titlesAndMotion = result;
        showAllScenes();

        // return result;
      }});
    });
});