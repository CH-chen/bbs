$(function () {
    $("#div_digg .action").click(function () {
        if ($(".info").attr("username")) {

            var is_up = $(this).hasClass("diggit");
            var article_id = $(".info").attr("article_id");


            $.ajax({
                url: "/blog/up_down/",
                type: "post",
                data: {
                    article_id: article_id,
                    is_up: is_up,
                    csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
                },

                success: (function (data) {
                    if (data.state) {
                        if (is_up) {
                            var diggnum_count = $("#digg_count").text();
                            diggnum_count = parseInt(diggnum_count) + 1;
                            $(".diggnum").text(diggnum_count);


                        } else {
                            var diggnum_count = $("#bury_count").text();
                            diggnum_count = parseInt(diggnum_count) + 1;
                            $("#bury_count").text(diggnum_count);

                        }


                    } else {
                        if (data.first_action) {
                            $("#digg_tips").html("你已经点赞过")
                        } else {
                            $("#digg_tips").html("你已经踩过")

                        }


                    }

                    setTimeout(function () {
                        $("#digg_tips").html("")

                    }, 1000)


                })
            })

        } else {
            location.href = "/login/"
        }

    })


});
