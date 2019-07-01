function add_iframe(url){
                   // $('<iframe />');  // Create an iframe element
                    var iframe=$('<iframe />', {
                        name: 'frame1',
                        id: 'frame1',
                        src: url,
                        frameborder: "0",
                        scrolling: "yes",
                        class: "libclips"
                    });
                  return   iframe
}


function ClipsStorageLogic(e, that, myVal){
var url=$(that).attr('href');
var data_style = JSON.parse($(that).attr('data-style'));
var data_post = JSON.parse($(that).attr('data-post'));
var storage_logic = data_post.storage_logic;
var csrf = data_post.csrfmiddlewaretoken;

if (storage_logic === 'true' && sessionStorage.getItem('folder_current_id')) {
  url = url + sessionStorage.getItem('folder_current_id') +'/';
}
 else {
  url = url + 1 + '/';
};

ajax_cascade_main( url, data_style, csrf);


$('.cms-toolbar-item-navigation-hover').removeClass();

e = e || window.event;
e.preventDefault();
e.stopPropagation();
e.stopImmediatePropagation();
}

function modal_catalog(ajx, url, style) {
    var Modal = CMS.Modal;
    var modal_clips  = new Modal({
       minWidth: style.minwidth,
       minHeight: style.minHeight,
        resizable: true,
        minimizable: true,
        maximizable: true
    });

    modal_clips.open({
        html: add_iframe(url),
      //  title: 'clip',
        width: style.width,
        height: style.height,
    });

    modal_clips.ui.modal.css(style);
$('.cms-structure').css("z-index", "132" );

$('.cms-modal-minimize').click(
function(){
if( $('html').hasClass('cms-modal-minimized') ) {
modal_clips.ui.modal.css( "z-index", "99999999" )
}
else {
modal_clips.ui.modal.css( "z-index", "140" );
}
}
);



$('.cms-modal-maximize').click(
function(){
if( !$('html').hasClass('cms-modal-maximized') ) {
modal_clips.ui.modal.css( "z-index", "140" );
} else {
modal_clips.ui.modal.css( "z-index", "9999999" );
}
}
);
}


function ajax_cascade_main(url, style, csrf) {
    var paramater;
    var tokenf = 'csrf';
    var postd = '{ "csrfmiddlewaretoken": "' + csrf + '" }';
    CMS.API.Helpers.csrf(tokenf);

    var data = {
        placeholder_id: 1,
        csrfmiddlewaretoken: CMS.config.csrf,
        target_language: CMS.config.request.language
    };
    $.ajax({
            type: 'POST',
            url: url,
            post: postd,
            data: data,
            success: function(response) {
                response;
                modal_catalog(response, url, style)
            }
        }
    );
}
