fetch('data.json')
    .then(response => response.json())
    .then(json => {
        var main = Handlebars.compile($("#main").html());
        Handlebars.registerPartial("courses", $("#courses").html());
        $("body").append(main(json));
    });
