Handlebars.registerHelper('ifObject', function(item, options) {
    if(typeof item === "object") {
        return options.fn(item);
    } else {
        return options.inverse(item);
    }
    });

Handlebars.registerHelper('getObjectName', function(object, key) {
    return Object.getOwnPropertyNames(object)[key];
    });   

fetch('data.json')
    .then(response => response.json())
    .then(json => {
        var element = $("#courses").html();
        var template = Handlebars.compile(element);
        $("#courses_placeholder").html(template(json));
    });