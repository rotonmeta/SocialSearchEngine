var num_box = 0;
var count = 0;
var filter = 'all';
var grid = [];
var slider_visibility = 0;
var age_val = 0;
var global_query = '';


var background = ['http://www.technocrazed.com/wp-content/uploads/2015/12/Wood-Wallpaper-Background-15.jpg', 'http://www.technocrazed.com/wp-content/uploads/2015/12/Wood-Wallpaper-Background-22.jpg', 'http://www.technocrazed.com/wp-content/uploads/2015/12/Wood-Wallpaper-Background-23.jpg', 'http://wallpoper.com/images/00/25/71/46/wood-textures_00257146.jpg', 'http://rustcrown.org/wp-content/uploads/2018/08/wood-texture-wallpaper-red-wood-texture-grain-natural-wooden-paneling-surface-photo-wood-texture-wallpaper-3d.jpg', 'http://rustcrown.org/wp-content/uploads/2018/08/wood-texture-wallpaper-home-fashions-texture-trends-ii-timber-x-wooden-texture-4k-wallpaper.jpg', 'https://upload.wikimedia.org/wikipedia/commons/4/40/Fraxinus_excelsior_wood_tangent_section_1_beentree.jpg', 'https://data.1freewallpapers.com/detail/wooden-fence.jpg'];

$(function () {
    $(document).ready(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

    $('.dropdown-menu a').eq(0).hide('fast');

    $(".dropdown-filters").click(function () {
        $('.dropdown-menu').slideToggle();
    });

    $(".dropdown-sliders").click(function () {

        $('.dropdown-menu').slideUp('fast');
        if (slider_visibility == 0) {
            $('.navbar').css('transition', 'box-shadow 0.05s ease-in-out');
            $('.navbar').css('box-shadow', '0 0px 2px -0.1px #aaaaaa');
            $('.sliders').slideDown('fast');
            $('.grid').css('padding-top', '210px');
            jQuery('.grid').masonry('reloadItems');
            jQuery('.grid').masonry('layout');

            slider_visibility = 1;
        } else {
            $('.sliders').slideUp('fast');
            $('.navbar').css('transition', 'box-shadow 0.4s ease-in-out');
            $('.navbar').css('box-shadow', '0 2px 10px -0.5px #aaaaaa');
            $('.grid').css('padding-top', '5%');
            jQuery('.grid').masonry('reloadItems');
            jQuery('.grid').masonry('layout');
            slider_visibility = 0;
        }

    });

    $(".all_filter").on("click", function () {
        $('.dropdown-menu').slideToggle('fast');
        num_box = 0;
        count = 0;
        filter = 'all';
        $('.dropdown-menu a').eq(0).hide('slow');
        $('.dropdown-menu a').eq(1).show();
        $('.dropdown-menu a').eq(2).show();
        $('.dropdown-menu a').eq(3).show();
        $('.dropdown-menu a').eq(4).show();
        $('.dropdown-filters').text('Filter by');
        callAjax();
    });
    $(".photo_filter").on("click", function () {
        $('.dropdown-menu').slideToggle('fast');
        num_box = 0;
        count = 0;
        filter = 'photo';
        $('.dropdown-menu a').eq(0).show('slow');
        $('.dropdown-menu a').eq(1).hide();
        $('.dropdown-menu a').eq(2).show();
        $('.dropdown-menu a').eq(3).show();
        $('.dropdown-menu a').eq(4).show();
        $('.dropdown-filters').text('Photo');
        callAjax();
    });
    $(".video_filter").on("click", function () {
        $('.dropdown-menu').slideToggle('fast');
        num_box = 0;
        count = 0;
        filter = 'video';
        $('.dropdown-menu a').eq(0).show('slow');
        $('.dropdown-menu a').eq(1).show();
        $('.dropdown-menu a').eq(2).hide();
        $('.dropdown-menu a').eq(3).show();
        $('.dropdown-menu a').eq(4).show();
        $('.dropdown-filters').text('Video');
        callAjax();
    });
    $(".page_filter").on("click", function () {
        $('.dropdown-menu').slideToggle('fast');
        num_box = 0;
        count = 0;
        filter = 'page';
        $('.dropdown-menu a').eq(0).show('slow');
        $('.dropdown-menu a').eq(1).show();
        $('.dropdown-menu a').eq(2).show();
        $('.dropdown-menu a').eq(3).show();
        $('.dropdown-menu a').eq(4).hide();
        $('.dropdown-filters').text('Page');
        callAjax();
    });
    $(".link_filter").on("click", function () {
        $('.dropdown-menu').slideToggle('fast');
        num_box = 0;
        count = 0;
        filter = 'link';
        $('.dropdown-menu a').eq(0).show('slow');
        $('.dropdown-menu a').eq(1).show();
        $('.dropdown-menu a').eq(2).show();
        $('.dropdown-menu a').eq(3).hide();
        $('.dropdown-menu a').eq(4).show();
        $('.dropdown-filters').text('Link');
        callAjax();
    });

    $("#add").on("click", function () {
        if (count == 0) {
            return;
        }
        num_box = num_box + 1;
        callAjax();
    });

    /* Hook enter to search */
    $("#query").keydown(function (e) {
        if (e.keyCode == '13') {
            $("html, body").animate({
                scrollTop: 0
            }, 600);
            num_box = 0;
            count = 0;
            callAjax();
        }
    });

});

function f(a) {
    propagation();
    var txt = $(a).attr('id');
    if (txt == 'page') {
        $(".page_filter").click();
    } else if (txt == 'link') {
        $(".link_filter").click();
    } else if (txt == 'photo') {
        $(".photo_filter").click();
    } else if (txt == 'video') {
        $(".video_filter").click();
    }
    $('.dropdown-menu').hide();
}

$('input[type="range"]').val(10).change();

function imgBig(t) {
    t.parentNode.classList.add('zoom');
}


function removezoom() {
    $('.grid-item').removeClass('zoom');
}

function redirect(e, link) {
    window.open(link);
    console.log($(e).closest('.grid-item').index());
    // click_index = $(e).closest('.grid-item').index();
    // $.ajax({
    //
    //     method: "GET",
    //
    //     url: "/",
    //
    //     data: {"query": global_query, "filter": filter, "click_index": click_index},
    //
    //     dataType: "text",
    //
    //     success: function (result) {
    //
    //         var data = JSON.parse(result);
    //         console.log(result);
    //
    //     }
    //
    // });


}

function propagation() {
    event.stopPropagation();
}


//     ----------------    PHOTO    ------------------------
function photo_square(content) {
    var box = $('<div class="grid-item"></div>');

    var inner_box = $('<div class="in"  onclick="redirect(this,\'' + content.image + '\')" onmouseover="imgBig(this)"  style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a><div class="icon" id="photo" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">photo_camera</i></div></a>');

    $(tags).append(icon);
    if (content.message != '__null__') {
        var tag = $('<a href="#" class="message">' + content.message + '</a>').css('margin-left', '8px');
        $(tags).append(tag);
    }
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(inner_box).append(tags);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}

function photo_width(content) {
    var box = $('<div class="grid-item grid-item--width"></div>');
    var inner_box = $('<div class="in in--width" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.image + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="photo" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">photo_camera</i></div></a>');

    $(tags).append(icon);
    if (content.message != '__null__') {
        var tag = $('<a href="#" class="message">' + content.message + '</a>').css('margin-left', '8px');
        $(tags).append(tag);
    }
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);
    var data_icon = $('<i class="fa fa-calendar-o" style="font-size:10px"></i>').css('margin-left', '10px');
    var datastring = String(content.data).substring(0, 10);
    var data = $('<div>' + datastring + '</div>').css('margin-left', '5px');


    $(user).append(data_icon);
    $(user).append(data);

    if (content.place_name != null && content.place_name != '__null__') {
        var place_icon = $('<i class="material-icons" style="font-size:11px">place</i>').css('margin-left', '10px');
        var place = $('<div>' + content.place_name + '</div>').css('margin-left', '5px');
        $(user).append(place_icon);
        $(user).append(place);
    }
    $(inner_box).append(tags);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}

function photo_height(content) {
    var box = $('<div class="grid-item grid-item--height"></div>');
    var inner_box = $('<div class="in in--height" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.image + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="photo" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">photo_camera</i></div></a>');

    $(tags).append(icon);
    if (content.message != '__null__') {
        var tag = $('<a href="#" class="message">' + content.message + '</a>').css('margin-left', '8px');
        $(tags).append(tag);
    }
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(inner_box).append(tags);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}
//     ----------------    VIDEO    ------------------------
function video_square(content) {
    var box = $('<div class="grid-item"></div>');
    var inner_box = $('<div class="in" onclick="redirect(this,\'' + content.link + '\')" onmouseover="imgBig(this)" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="video" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">videocam</i></div></a>');

    $(tags).append(icon);
    if (content.message != '__null__' &&
        content.message != null) {
        var tag = $('<a href="#" class="message">' + content.message + '</a>').css('margin-left', '8px');
        $(tags).append(tag);
    }
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);


    $(inner_box).append(tags);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}
//     ----------------    VIDEO_LINK    ------------------------
function video_link_width(content) {
    var box = $('<div class="grid-item grid-item--width"></div>');
    var image = $('<div class="in onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var right = $('<div class="in " onmouseover="imgBig(this)" ></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="video" onClick="f(this);" style="background-color:black"><i class="material-icons" style="color:white">videocam</i></div></a>');
    $(tags).append(icon);
    var text = $('<div class="text"></div>')
    var title = $('<a href="#"  ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div style="color:#818181" onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(right).append(tags);
    $(text).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(text).append(description);
    }
    $(right).append(text);
    $(right).append(user);

    $(box).append(image);
    $(box).append(right);
    return box;
}

function video_link_height(content) {
    var box = $('<div class="grid-item grid-item--height"></div>').css('display', 'inline-block');
    var image = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')').css('box-shadow', '0 2px 10px -3px #aaaaaa').css('height', '260px').css('margin-left', '20px').css('margin-top', '20px');
    var text = $('<div class="in " onmouseover="imgBig(this)" ></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('height', '260px').css('margin-left', '20px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="video" onClick="f(this);" style="background-color:black"><i class="material-icons" style="color:white">videocam</i></div></a>');
    $(tags).append(icon);
    var t = $('<div class="text  text-height"></div>');
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div style="color:#818181" onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(t).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(t).append(description);
    }

    $(text).append(tags);
    $(text).append(t);
    $(text).append(user);

    $(box).append(image);
    $(box).append(text);
    return box;
}

function video_link_square(content) {
    var box = $('<div class="grid-item"></div>');
    var inner_box = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + content.image + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="video" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">videocam</i></div></a>');
    var title = $('<a href="#" ><div class="title title_white" ><span>' + content.name + '</span></div></a>').css('padding-top', '4px').css('text-decoration', 'none').css('text-shadow',' 0 0 10px rgba(0,0,0,1)');
    $(tags).append(icon);
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);


    $(inner_box).append(tags);
    $(inner_box).append(title);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}
//     ----------------    LINK    ------------------------
function link_width(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item grid-item--width"></div>');
    var image = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + image_str + ')').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var right = $('<div class="in " onmouseover="imgBig(this)"></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="link" onClick="f(this);" style="background-color:black"><i class="material-icons" style="color:white">insert_link</i></div></a>');
    $(tags).append(icon);
    var text = $('<div class="text"></div>')
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div style="color:#818181" onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(right).append(tags);
    $(text).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(text).append(description);
    }
    $(right).append(text);
    $(right).append(user);

    $(box).append(image);
    $(box).append(right);
    return box;
}

function link_height(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item grid-item--height"></div>').css('display', 'inline-block');
    var image = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + image_str + ')').css('box-shadow', '0 2px 10px -3px #aaaaaa').css('height', '260px').css('margin-left', '20px').css('margin-top', '20px');
    var text = $('<div class="in " onmouseover="imgBig(this)" ></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('height', '260px').css('margin-left', '20px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="link" onmouseover="imgBig(this)" onClick="f(this);" style="background-color:black"><i class="material-icons" style="color:white">insert_link</i></div></a>');
    $(tags).append(icon);
    var t = $('<div class="text  text-height"></div>');
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div style="color:#818181" onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(t).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(t).append(description);
    }

    $(text).append(tags);
    $(text).append(t);
    $(text).append(user);

    $(box).append(image);
    $(box).append(text);
    return box;
}

function link_square(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item"></div>');
    var inner_box = $('<a class="in" onmouseover="imgBig(this)" href="#" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"> <div ></div></a>').css('background-image', 'url(' + image_str + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="link" onClick="f(this);" style="background-color:white"><i class="material-icons" style="color:black">insert_link</i></div></a>');
    var title = $('<a href="#" ><div class="title title_white" >' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none').css('text-shadow',' 0 0 10px rgba(0,0,0,1)');
    $(tags).append(icon);
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);


    $(inner_box).append(tags);
    $(inner_box).append(title);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}
//     ----------------    FB_PAGE    ------------------------
function page_width(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item grid-item--width"></div>');
    var image = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + image_str + ')').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var right = $('<div class="in " onmouseover="imgBig(this)" ></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('width', '260px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="page" onClick="f(this);" style="background-color:black"><i class="fa fa-facebook" style="color:white"></i></div></a>');

    if (content.genre != '__null__' &&
        content.genre != null) {
        var str_tag = content.genre;
    } else {
        //var tmp_str_tag = content.category_list[0].split(": ");
        //var str_tag = tmp_str_tag[2].replace(/}/g,"").replace(/'/g,"");
        var str_tag = '_da_aggiustare_'
    }
    var tag = $('<a href="#" onClick="propagation();" class="tag">' + str_tag + '</a>').css('margin-left', '4px');
    $(tags).append(icon);
    $(tags).append(tag);
    var text = $('<div class="text"></div>')
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');

    $(right).append(tags);
    $(text).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(text).append(description);
    }
    $(right).append(text);

    $(box).append(image);
    $(box).append(right);
    return box;
}

function page_height(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item grid-item--height"></div>').css('display', 'inline-block');
    var image = $('<div class="in" onmouseover="imgBig(this)" onclick="redirect(this,\'' + content.link + '\')" style="cursor: pointer"></div>').css('background-image', 'url(' + image_str + ')').css('box-shadow', '0 2px 10px -3px #aaaaaa').css('height', '260px').css('margin-left', '20px').css('margin-top', '20px');
    var text = $('<div class="in " onmouseover="imgBig(this)" ></div>').css('box-shadow', '0 2px 10px -0.5px #aaaaaa').css('height', '260px').css('margin-left', '20px');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" id="page" onClick="f(this);" style="background-color:black"><i class="fa fa-facebook" style="color:white"></i></div></a>');
    if (content.genre != '__null__' &&
        content.genre != null) {
        var str_tag = content.genre;
    } else {
        //var tmp_str_tag = content.category_list[0].split(": ")
        // var str_tag = tmp_str_tag[2].replace(/}/g,"").replace(/'/g,"");
        var str_tag = '_da_aggiustare_'

    }
    var tag = $('<a href="#" onClick="propagation();" class="tag">' + str_tag + '</a>').css('margin-left', '4px');
    $(tags).append(icon);
    $(tags).append(tag);
    var t = $('<div class="text  text-height"></div>');
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title">' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none');
    var description = $('<div class="description">' + content.description + '</div>');

    $(t).append(title);
    if (content.description != '__null__' &&
        content.description != null) {
        $(t).append(description);
    }

    $(text).append(tags);
    $(text).append(t);

    $(box).append(image);
    $(box).append(text);
    return box;
}

function page_square(content) {
    if (content.image != 'None') {
        var image_str = content.image;
    } else {
        var image_str = 'http://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg';
    }
    var box = $('<div class="grid-item"></div>');
    var inner_box = $('<a class="in" href="#" onclick="redirect(this,\'' + content.link + '\')" onmouseover="imgBig(this)"  style="cursor: pointer"> <div ></div></a>').css('background-image', 'url(' + image_str + ')').css('box-shadow', '0 2px 10px -0.5px #aaaaaa, inset 1000px 4000px 1200px rgba(0,0,0,0.1)');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#"  ><div class="icon" id="page" onClick="f(this);" style="background-color:white"><i class="fa fa-facebook" style="color:black"></i></div></a>');
    var title = $('<a href="#" ><div onclick="redirect(this,\'' + content.link + '\')" class="title title_white" >' + content.name + '</div></a>').css('padding-top', '4px').css('text-decoration', 'none').css('text-shadow',' 0 0 10px rgba(0,0,0,1)');

    if (content.genre != '__null__' &&
        content.genre != null) {
        var str_tag = content.genre;
    } else {
        //var tmp_str_tag = content.category_list[0].split(": ");
        //var str_tag = tmp_str_tag[2].replace(/}/g,"").replace(/'/g,"");
        var str_tag = '_da_aggiustare_'
    }
    var tag = $('<a href="#" onClick="propagation();" class="tag">' + str_tag + '</a>').css('margin-left', '4px');
    $(tags).append(icon);
    $(tags).append(tag);


    $(inner_box).append(tags);
    $(inner_box).append(title);

    $(box).append(inner_box);
    return box;
}
//     ----------------    POST    ------------------------
function post_square(content) {
    var box = $('<div class="grid-item"></div>');
    var url = random_background();
    var inner_box = $('<a href="#" class="in" onmouseover="imgBig(this)" style="cursor: pointer"> <div ></div></a>').css('background-image', 'url(' + url + ')');
    var tags = $('<div class="tags"></div>');
    var icon = $('<a href="#" ><div class="icon" style="background-color:white"><i class="fa fa-pencil-square-o" style="color:black"></i></div></a>');
    var text = $('<div class="text-status" >' + content.message + '</div>').css('text-decoration', 'none').css('text-shadow',' 0 0 10px rgba(0,0,0,1)');
    $(tags).append(icon);
    var user = $('<div class="user"></div>');
    var user_name = $('<div class="profpic"><a  href="' + content.user_profile_picture + '" target="_blank"><img onClick="propagation();" src="' + content.user_profile_picture + '"></img></a></div><a href="' + content.user_profile_picture + '" target="_blank" ><div  onClick="propagation();">' + content.user_name + '</div></a>').css('margin-left', '5px');
    $(user).append(user_name);

    $(inner_box).append(tags);
    $(inner_box).append(text);
    $(inner_box).append(user);

    $(box).append(inner_box);
    return box;
}

function random_background() {
    for (j = 0; j < Math.floor((Math.random() * 4) + 2); j++) {
        var num = Math.floor((Math.random() * 8) + 0);
    }
    return background[num];
}


function callAjax() {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    } else {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var docs = JSON.parse(xmlhttp.response).response.docs;
            render(docs, 0);
        }
    }
    var searchStr = document.getElementById("query");
    var start = num_box * 12
    if (searchStr.value.length == 0) {
        return;
    } else if (filter == 'all') {
        var query_filter = '';
    } else if (filter == 'photo') {
        var query_filter = 'type:photo AND ';
    } else if (filter == 'video') {
        var query_filter = '(type:video OR type:video_link) AND ';
    } else if (filter == 'page') {
        var query_filter = '(type:page) AND ';
    } else if (filter == 'link') {
        var query_filter = '(type:link) AND ';
    } else {
        return;
    }
    var query = searchStr.value;
    if (query.includes(' ')==true){
        query='"'+query+'"';
    }else{
        query=query;
    }
    console.log(query);
    global_query=query;
    var score_weight = " ";
    var tmp_user_list = [];
    var tmp_user_score = [];
    for (i = 0; i < (score_list.length); i++) {
        var score = parseFloat(score_list[i].score);
        var weight = document.getElementById(String(score_list[i].type)).value;
        score = score * parseFloat(weight);
        if (tmp_user_list.indexOf(score_list[i].user_id) == -1) {
            tmp_user_list.push(score_list[i].user_id);
            tmp_user_score.push({
                'user_id': score_list[i].user_id,
                'score': score
            });
        } else {
            for (j = 0; j < (tmp_user_score.length); j++) {
                if (tmp_user_score[j].user_id == score_list[i].user_id) {
                    if (score > tmp_user_score[j].score) {
                        tmp_user_score[j].score = score;
                        break;
                    }
                }
            }
        }
    }
    for (i = 0; i < (tmp_user_score.length); i++) {
        score_weight = score_weight + 'user_id:*' + tmp_user_score[i].user_id + '*^' + (tmp_user_score[i].score + 12) + ' OR ';
    }
    if (score_list.length == 0) {
        score_weight = '';
    } else {
        score_weight = " and (user_id:*" + String(user_id) + "*^-10000 OR " + score_weight.substr(0, score_weight.length - 3) + ')^150 ';
    }
    console.log(score_weight);
    xmlhttp.open("GET", solr
        + 'select?q=doc_type:content AND '
        + query_filter
        + '(name:' + query + '^10 and place_name:' + query + '^9 and genre:' + query + '^8 and category_list:' + query + '^7 and description:' + query + '^6 and message:' + query + '^5 and city:' + query + '^4 and country:' + query + '^3)^0 '
        + score_weight + ' &start=' + start + '&rows=13', true);
    xmlhttp.send();
}
function AjaxUpdateScore() {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    } else {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var docs = JSON.parse(xmlhttp.response).response.docs;
            updateScore(docs, 0);
        }
    }
    xmlhttp.open("GET", solr + 'select?q=doc_type:score -score:0 AND (userA:'+user_id+' OR userB:'+user_id+')& rows=130000', true);
    xmlhttp.send();
}
function updateScore(arr){
    var tmp_score_list=[];
    for (i = 0; i < arr.length; i++) {
        var doc={};
        if (String(arr[i].userA)==user_id){
                var second_user=arr[i].userB;
        }else{
                var second_user=arr[i].userA;
        }
        doc['user_id']=String(second_user);
        doc['score']=arr[i].score;
        if (String(arr[i].type).includes('places_')){
                var type='place';
        }else if (String(arr[i].type).includes('age_')){
                var type='age';
        }else if (String(arr[i].type).includes('books_')){
                var type='book';
        }else if (String(arr[i].type).includes('music_')){
                var type='music';
        }else if (String(arr[i].type).includes('television_')){
                var type='TV';
        }else if (String(arr[i].type).includes('movies_')){
                var type='movie';
        }else if (String(arr[i].type).includes('generic_')){
                var type='page';
        }
        doc['type']=type;
        tmp_score_list.push(doc);
    }
    score_list=tmp_score_list;
}
function render(arr, n) {
    removezoom();
    if (num_box == 0) {
        $(".grid").empty();
    }
    if (arr.length == 13) {
        var correct = 1;
    } else {
        var correct = 0;
    }
    var V = [];
    for (i = 0; i < (arr.length - correct); i++) {
        if (arr[i].type == 'photo') {
            if (arr[i].aspect_ratio > 1.3) {
                var box = photo_width(arr[i]);
                count = count + 2;
                V.push(i);
            } else if (arr[i].aspect_ratio < 0.7) {
                var box = photo_height(arr[i]);
                count = count + 2;
                V.push(i);
            } else {
                var box = photo_square(arr[i]);
                count = count + 1;
            }



        } else if (arr[i].type == 'video') {
            var box = video_square(arr[i]);
            count = count + 1;

        } else if (arr[i].type == 'video_link') {
            for (j = 0; j < Math.floor((Math.random() * 3) + 1); j++) {
                var num = Math.floor((Math.random() * 2) + 1);
            }
            if (num == 1) {
                var box = video_link_width(arr[i]);
            } else {
                var box = video_link_height(arr[i]);
            }

            count = count + 2;
            V.push(i);

        } else if (arr[i].type == 'link') {
            for (j = 0; j < Math.floor((Math.random() * 3) + 1); j++) {
                var num = Math.floor((Math.random() * 2) + 1);
            }
            if (num == 1) {
                var box = link_width(arr[i]);
            } else {
                var box = link_height(arr[i]);
            }
            count = count + 2;
            V.push(i);

        } else if (arr[i].type == 'page') {
            for (j = 0; j < Math.floor((Math.random() * 3) + 1); j++) {
                var num = Math.floor((Math.random() * 2) + 1);
            }
            if (num == 1) {
                var box = page_height(arr[i]);
            } else {
                var box = page_width(arr[i]);
            }
            count = count + 2;
            V.push(i);

        } else if (arr[i].type == 'status') {
            var box = post_square(arr[i]);
            count = count + 1;
        }
        $(box).css({
            opacity: 0
        });
        $(".grid").append(box);
    }
    jQuery('.grid').masonry('reloadItems');
    jQuery('.grid').masonry('layout');
    var y = $('.grid').height() / 280;

    var num_elements = num_box * 12;
    y = (y * 4).toFixed();
    if (y != count) {
        for (k = 0; k < Math.floor((Math.random() * 3) + 1); k++) {
            V = shuffle(V);
        }
        var n = 0;
        for (i = 0; i < V.length; i++) {
            var n = n + 1;
            var cell = window[arr[V[i]].type + "_square"](arr[V[i]]);
            $(cell).css({
                opacity: 0
            });
            $('.grid-item').eq(num_elements + V[i]).replaceWith($(cell));
            count = count - 1;
            jQuery('.grid').masonry('reloadItems');
            jQuery('.grid').masonry('layout');
            y = $('.grid').height() / 280;
            y = (y * 4).toFixed();
            if (y == count) {
                break;
            }
        }

    }
    if (correct == 1) {
        $('.load').show().css('opacity', '0');
        $('.load').delay(400).animate({
            opacity: 1
        }, 250);
    } else {
        $('.load').hide();
    }
    show_grid(num_elements, arr.length - correct);
    removezoom();
    AjaxUpdateScore();
}


function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        for (k = 0; k < Math.floor((Math.random() * 3) + 1); k++) {
            j = Math.floor(Math.random() * (i + 1));
        }
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

function show_grid(bottom, top) {
    for (i = 0; i < top; i++) {
        $('.grid-item').eq(bottom + i).delay((i + 1) * 100).animate({
            opacity: 1
        }, 150);
    }
}
