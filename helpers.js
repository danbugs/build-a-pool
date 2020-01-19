Handlebars.registerHelper('ifObject', function(item, options) {
    if(typeof item === "object") {
        return options.fn(item);
    } else {
        return options.inverse(item);
    }
    });

Handlebars.registerHelper('getObjectName', function(object) {
    return Object.getOwnPropertyNames(object);
    });   

Handlebars.registerHelper('getObject', function(object) {
        return JSON.stringify(object);
        }); 
