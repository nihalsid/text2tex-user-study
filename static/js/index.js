// const SURVEY_ID = 1;

$( document ).ready(function() {

    function alertResults (sender) {
//        const results = JSON.stringify(sender.data);
//        alert(results);
        // saveSurveyResults(
        //     "https://your-web-service.com/" + SURVEY_ID,
        //     sender.data
        // )
//        $.ajax({
//            type: "PUT",
//            url: "submit",
//            contentType: "application/json",
//            data: JSON.stringify(sender.data)
//        });
        $.ajax({
            url: "submit",
            type: "get",
            data: sender.data,
        });
    }

    $(function() {
        $.get( "form", function( data ) {
          var survey = new Survey.Model(data);
          survey.onComplete.add(alertResults);
          $("#surveyContainer").Survey({ model: survey });
        });
    });
});
