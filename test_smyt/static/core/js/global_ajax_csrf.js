
$(function(){ 
    $.ajaxSetup({
        headers: {'X-CSRFToken': test_smyt.csrf_token }
    });

    var oldSync = Backbone.sync;
    Backbone.sync = function(method, model, options){
      options.beforeSend = function(xhr){
        xhr.setRequestHeader('X-CSRFToken', test_smyt.csrf_token);
      };
      return oldSync(method, model, options);
    };
})
