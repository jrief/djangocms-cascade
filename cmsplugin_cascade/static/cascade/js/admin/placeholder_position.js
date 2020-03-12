function set_placeholder_to_first_child_position(title, cms_structure_content){
    //Quick way to move placeholder selected by string name as first child position in cms structure mode 
    var p_header_title = `.cms-dragbar-title[title="${title}"]`
    var p_header_cms_dragbar = document.querySelectorAll(p_header_title)[0];
    var p_header_cms_dragarea = p_header_cms_dragbar.parentNode.parentNode;
    var isfirstchild = (p_header_cms_dragarea ==  p_header_cms_dragarea.parentNode.firstChild);
    if (cms_structure_content.classList.contains('empty') || p_header_cms_dragbar && !isfirstchild ){
    cms_structure_content.prepend(p_header_cms_dragarea); 
    }
};

function placeholder_position_top(title_placeholder){
    var cms_structure_content = document.querySelectorAll('.cms-structure-content')[0];
    var observer = new MutationObserver(function(e) { set_placeholder_to_first_child_position(title_placeholder,cms_structure_content);});
    observer.observe(cms_structure_content, { childList: true});
};

