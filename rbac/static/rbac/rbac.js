/**
 * Created by haier on 2017-12-02.
 */

$(".item_permission").on("click", function () {
    if ($(this).next().hasClass("hides")) {
        $(this).next().removeClass("hides")
    }
    else {
        $(this).next().addClass("hides")
    }
});