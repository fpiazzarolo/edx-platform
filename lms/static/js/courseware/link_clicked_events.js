;(function(define) {
    'use strict';

    define(['jquery', 'logger'], function ($, Logger) {
        return function () {
            $('a:not([href^="#"])').click(function(event) {
                var parents = $(event.currentTarget).parents(".xblock");
                var parent_id = "courseware";
                if (parents.length == 0) {
                    if($(event.currentTarget).parents(".course-navigation")){
                        parent_id = "course_navigation";
                    }
                }
                else{
                    parent_id = parents.first().attributes.data_usage_id;
                }
                Logger.log(
                    "edx.ui.lms.link_clicked",
                    {
                        current_url: window.location.href,
                        target_url: event.currentTarget.href,
                        containing_element: parent_id
                    });
            });
        };
    });
}).call(this, define || RequireJS.define);
