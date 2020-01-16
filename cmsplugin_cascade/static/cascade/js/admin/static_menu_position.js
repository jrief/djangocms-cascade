//Move static_placeholder "Navbar Content" as first-child in structure ui
//Todo : make this as templatetag  
function static_placeholder_menu_gofirstchild(){
if ($(".cms-structure-content").is(':empty') || $(".cms-dragbar-title[title='Navbar Content']") && !$(".cms-dragbar-title[title='Navbar Content']").parent().parent().is(':first-child') ) {
$(".cms-dragbar-title[title='Navbar Content']").parent().parent().prependTo(".cms-structure-content");}
}
$(document).ready(function(){
var observer = new MutationObserver(function(e) {static_placeholder_menu_gofirstchild();});
observer.observe($('.cms-structure-content')[0], { childList: true});
});
