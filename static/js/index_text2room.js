// const SURVEY_ID = 1;

$( document ).ready(function() {

    function alertResults (sender) {
        $.ajax({
            url: "submit_text2room",
            type: "get",
            data: sender.data,
        });
    }

    $(function() {
        $.get( "form_text2room", function( data ) {
          var survey = new Survey.Model(data);
          survey.onComplete.add(alertResults);
          $("#surveyContainer").Survey({ model: survey });
        });
    });
});
