DATA = {"turn_logs":[], "players": [{"name": "Blue", "firstdieroll": 0, "seconddieroll": 0, "firstdiereroll": 0, "seconddiereroll": 0, "scorethisround": 0, "totalscore": 0, "passed": false}], "turn": 0, "step": 0, "phase": 0}
RESOURCES = ['food','wood','stone','cloth','gold']
TRACKS = [
    ["{P1}", "{P2}", "{P3}", "{P4}", "{P5}"],
    ["{$3}", "{$4}", "{$5}", "{$6}", "{$7}"],
    ["{F}", "{W}/{S}", "{C}", "{R}->{R2}", "{G}"],
    ["-", "Carp", "Mason", "Lawyer", "Arch"]
]
PLAYERS = ['Blue', 'Red', 'Green', 'Orange', 'Black']
GAME_ID = null
PLAYER_ID = null
DIALOG = null
SINGLE_PLAYER = null


IMAGES = {
    "{\\$b}": "/static/img/icons/money/blank.png",
    "{\\$1}": "/static/img/icons/money/1.png",
    "{\\$2}": "/static/img/icons/money/2.png",
    "{\\$3}": "/static/img/icons/money/3.png",
    "{\\$4}": "/static/img/icons/money/4.png",
    "{\\$5}": "/static/img/icons/money/5.png",
    "{\\$6}": "/static/img/icons/money/6.png",
    "{\\$7}": "/static/img/icons/money/7.png",
    "{Pb}": "/static/img/icons/points/blank.png",
    "{P1}": "/static/img/icons/points/1.png",
    "{P2}": "/static/img/icons/points/2.png",
    "{P3}": "/static/img/icons/points/3.png",
    "{P4}": "/static/img/icons/points/4.png",
    "{P5}": "/static/img/icons/points/5.png",
    "{P6}": "/static/img/icons/points/6.png",
    "{P7}": "/static/img/icons/points/7.png",
    "{P8}": "/static/img/icons/points/8.png",
    "{P9}": "/static/img/icons/points/9.png",
    "{P-1}": "/static/img/icons/points/-1.png",
    "{P-2}": "/static/img/icons/points/-2.png",
    "{P-3}": "/static/img/icons/points/-3.png",
    "{P-4}": "/static/img/icons/points/-4.png",
    "{F}": "/static/img/icons/cubes/food.png",
    "{F2}": "/static/img/icons/cubes/food2.png",
    "{W}": "/static/img/icons/cubes/wood.png",
    "{W2}": "/static/img/icons/cubes/wood2.png",
    "{S}": "/static/img/icons/cubes/stone.png",
    "{S2}": "/static/img/icons/cubes/stone2.png",
    "{C}": "/static/img/icons/cubes/cloth.png",
    "{C2}": "/static/img/icons/cubes/cloth2.png",
    "{C3}": "/static/img/icons/cubes/cloth3.png",
    "{G}": "/static/img/icons/cubes/gold.png",
    "{G2}": "/static/img/icons/cubes/gold2.png",
    "{R}": "/static/img/icons/cubes/any.png",
    "{R2}": "/static/img/icons/cubes/any2.png",
    "{R4}": "/static/img/icons/cubes/any4.png",
    "{Fs}": "/static/img/icons/cubes/small/food.png",
    "{Ws}": "/static/img/icons/cubes/small/wood.png",
    "{Ss}": "/static/img/icons/cubes/small/stone.png",
    "{Cs}": "/static/img/icons/cubes/small/cloth.png",
    "{Gs}": "/static/img/icons/cubes/small/gold.png"


}

function update_received(message){
    //if(DIALOG){
    //    DIALOG.dialog('close')
    //    DIALOG = null
    //}
    DATA = $.parseJSON(message)
    update_board()
    //show_decision()
}

function show_connect_dialog(){
    var dialog = $('<div></div>')
    dialog.append('<div id="tabs2"><ul><li><div id="sp">Start Solo Game</div></li><li><a href="#mult">Multiplayer</a></li><li><a href="#tutorial">Tutorial</a></li></ul><div id="mult">Multiplayer</div><div id="tutorial">Tutorial</div></div>');
  
    dialog.dialog({
        draggable: false,
        resizable: false,
        show: 'fade',
        hide: 'fade',
        modal: true,
        height: 370,
        width: 450,
        //position: ['center', 35],
        open: function() {
            $('#tabs2').tabs({
            active: 0
            });
            $(function() {
            $( "#sp" )
            .button()
            .click(start_sp);
            });
            $(this).parent().children('.ui-dialog-titlebar').remove();
        }
    });
    dialog.dialog('open');
    DIALOG = dialog
    
}
function post_to_url(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}
function start_sp(){

    PLAYER_ID = "none";
    PLAYER = "none";
    GAME_ID = getRandom(1,100000);
    SINGLE_PLAYER = true;
    params = {'type':"START",
        'id':GAME_ID,
              'player':2,
              'create':"none",
              'sp': 1}
    dialog = DIALOG
    DIALOG = null
    dialog.dialog('close');
    post_to_url("/play", params, "post");

    /*
    $.getJSON('play', params, function(data) {
        dialog.dialog('close');
    });
    */

}

function rerolldice(){
    alert(dice);


}


function init_board(){
    //make the columns the correct width etc.
    $('#leftside').prepend('<div class="span3">\
                <table class="table table-hover table-striped">\
                    <tbody id = "scoretable">\
                        <tr><td><span class="label label">Turn</span></td>\
                            <td><span class="label label-important">Bot\'s Turn</span></td>\
                            <td><span class="label label-info">Your Turn</span></td>\
                        </tr>\
                        <tr class = "success" id = "total"><td>TOTAL:</td>\
                            <td>5</td>\
                            <td>3</td>\
                        </tr>\
                    </tbody>\
                </table>\
            </div>');
}

function update_board(){
    /*turn_order = ''
    for(var i=0; i<DATA.players.length; i++){
        turn_order += DATA.players[i].name + '<br>';
    }
    $('#order').html(turn_order)*/

    // Update logs

    //update table  
    $('#scoretable').append('<tr><td>'+(DATA.turn+1)+'</td>\
                            <td>'+DATA.players[1].firstdieroll + '/'+DATA.players[1].seconddieroll+'</td>\
                            <td>'+DATA.players[0].firstdieroll + '/'+DATA.players[0].seconddieroll+'</td>\
                        </tr>');
    $('#scoretable').append( $("#total"));                    
            
    //update text
    $('#firstroll').html(DATA.players[0].firstdieroll);
    $('#secondroll').html(DATA.players[0].seconddieroll);
    

}

function getRandom(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
}

function perform_connect(){
    PLAYER_ID = $('#create').is(':checked') ? 0 : parseInt($('#player').val());
    PLAYER = PLAYERS[PLAYER_ID]
    GAME_ID = $('#game-id').attr('value')
    params = {'id':$('#game-id').attr('value'),
              'player':$('#player').attr('value'),
              'create':($('#create').is(':checked') ? '1' : '0')}
    $('.ui-dialog-content').text('Connecting... ' )
    //dialog = DIALOG
    //DIALOG = null
    $.getJSON('connect', params, function(data) {
        //dialog.dialog('close')
        DATA = data
        init_board()
        update_board()
        updater.update_received = update_received
        updater.id = GAME_ID
        updater.poll();
    });
}



$(document).ready(function(){
    setTimeout(show_connect_dialog, 1000);

    $('.b').click(function(){
        if($(this).hasClass('available')){
            $('.b').removeClass('available')
            submit_decision($(this).attr('i'))
        }
    })
    //DECISION = ACTION_DECISION
    //show_action_decision()
});