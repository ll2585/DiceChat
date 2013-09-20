// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.
var myId = null;
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").on("submit", function() {
        return false;
    });
    updateButtonHandlers();
   //this starts the message buffer that waits for new messages
    updater.poll();

    var iloaded = {'load_find': true, 'gameid': $("#gameid").html()};
    $.postJSON("/a/loaded", iloaded, function(response){
        myId = response.activeplayerID;
        console.log(response);
        console.log(response.activeplayerID);
    });
    redrawScoreboard();
});


function redrawScoreboard(){
    $('.scoreboard').offset({ top: ($( document ).height() - $('.scoreboard').height()) });
}

function updateButtonHandlers(){
     $("#rr1, #rr2, #rrend, #start, .gameButton").on("click", function(event) {
        var message = $(this).formToDict();
        var thisbutton = this;
        console.log("sending...");
        console.log(message);
        //sends a message, gets a response back if it was sent or not
        $.postJSON("/a/action", message, function(response) {
            /*if($(thisbutton).attr("id") == "rr1" || "rr2"){
                console.l
                $(thisbutton).remove();
            } else{

            }*/
            window.console.log("response: ");
            window.console.log(response);
            if(response['rerolled1']){
                $("#rr1").remove();
            }
            if(response['rerolled2']){
                $("#rr2").remove();
            }
            if(response['start']){
                $("#start").remove();
            }
            if(response['waiting']){
                $("#rr1, #rr2, #rrend").remove();
                $("#buttons").append("<div id = 'waiting'><p>WAITING</p></div>");
            }
            updater.showMessage(response);
            if (message.id) {
                form.parent().remove();
            } else {

            }
        });
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
            success: function(response) {
        if (callback) callback(eval("(" + response + ")"));
    }, error: function(response) {
        console.log("ERROR:", response)
    }});
};


jQuery.fn.formToDict = function() {
    //seralizes aka makes the form into a json (this has no effect except putting the cookie into json)
    var formData = $(this).closest('form').serializeArray();
    //this pushes the button onto the form; here we are setting ["action"] equal to the name of the button (div name)
    formData.push({name: "action", value: $(this).attr("name") });
    if($(this).attr("name") == "reroll_1"){
        formData.push({name: "dicenum", value: 0 });
    }else if($(this).attr("name") == "reroll_2"){
        formData.push({name: "dicenum", value: 1 });
    }
    //this also adds the game id
    formData.push({name: "gameid", value: $("#gameid").html() });
    var fields = formData;
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        //convert it to json
        json[fields[i].name] = fields[i].value;
    }
    //return the json
    if (json.next) delete json.next;
    return json;
};

jQuery.fn.disable = function() {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function(opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};

var updater = {
    errorSleepTime: 500,
    cursor: null,

    poll: function() {
        var args = {"_xsrf": getCookie("_xsrf")};
        args.gameid = $("#gameid").html();
        if (updater.cursor) args.cursor = updater.cursor;
        console.log("polling...");
        console.log($.param(args));
        $.ajax({url: "/a/action/updates", type: "POST", dataType: "text",
                data: $.param(args), success: updater.onSuccess,
                error: updater.onError});
    },

    onSuccess: function(response) {
        console.log("THE RESPONES IS");
        console.log(response);
        try {
            console.log("OK!");
            updater.newMessages(eval("(" + response + ")"));
        } catch (e) {
            updater.onError();
            return;
        }
        updater.errorSleepTime = 500;

        window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newMessages: function(response) {
        console.log("NEW RESPONSE!");
        console.log("the response length is " +        response.messages.length);
        console.log(response);
        var s = response.messages.length - 1;
            //if its not me, and its done, my turn !
            if(response.messages[s].currentPlayer == myId){
                //if the other guy is over my turn !

                $("#waiting").remove();
                $("#buttons").append('<input type="submit" id = "rr1" name="reroll_1" value="Reroll ' + response.messages[s].dice1 + '">\
              <input type="submit" id = "rr2" name="reroll_2" value="Reroll ' + response.messages[s].dice2 + '">\
              <input type="submit" id = "rrend" name="end_turn" value="End">');
                updateButtonHandlers();
            }
            if(response.messages[s].players_in_game >= 2){
                //game started!
                $("#start").removeAttr('disabled');
            }
            if(response.messages[s].started){
                //game started!
                $("#start").remove();
                $("#addBot").remove();
            }
            if(response.messages[s].scores){
                console.log("POLL ERROR??");
                //alert(response.messages[s].scores);
                //update scores
                console.log(response.messages[s].scores.scoreboard);
                var scores = [
                    {"name": "Luke", "score": 49},
                    {"name": "Bob", "score": 4},
                ];
                scores = response.messages[s].scores.scoreboard;
                /*
                var tbody = $('.scoreboard tbody'),
                props = ["name", "score"];
                $.each(scores, function(i, s) {
                  var tr = $('<tr>');
                  $.each(props, function(i, prop) {
                    $('<td>').text(s[prop]).appendTo(tr);  
                  });
                  tbody.append(tr);
                });*/
                var objUser = {"id":2,"username":"j.smith","fname":"john","lname":"smith"};
                var objKeys = ["name", "score", "lname"];
                for(var f =0; f < scores.length; f++){
                    $('#tr_' + scores[f].id + ' td').each(function(i) {
                        $(this).text(scores[f][objKeys[i]]);
                    });
                }

                console.log("ADDED SCORES??");

            }
            if(response.messages[s].other_player_joined){
                //game started!
                var toappend = '<tr id = "tr_' +response.messages[s].joinerid+'"><td>' + response.messages[s].joinername+ '</td><td>'+ response.messages[s].joinerscore +'</td></tr>';
                //toappend.hide();
                $(".scoreboard-table").append(toappend);
                //toappend.slideDown();
                console.log('appended ' + toappend);
                redrawScoreboard();
            }
        if (!response.messages) return;
        updater.cursor = response.cursor;
        var messages = response.messages;
        updater.cursor = messages[messages.length - 1].id;
        console.log(messages.length, "new messages, cursor:", updater.cursor);
        for (var i = 0; i < messages.length; i++) {
            updater.showMessage(messages[i]);
        }
    },

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
        redrawScoreboard();
    }
};


function highlight(element){
    $(element).css("background-color", "red");
}