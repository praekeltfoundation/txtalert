
jQuery.fn.james=function(url_to_call,options){var that=jQuery(this),results_set=[],current_hovered_rank=0,keyEvents=[{keycode:38,action:function(){keyEventKeyUp();}},{keycode:40,action:function(){keyEventKeyDown();}},{keycode:13,action:function(){keyEventEnter();}},{keycode:27,action:function(){keyEventEsc();}}],ul_element=false,o=jQuery.extend({onKeystroke:function(data){return data;},onSelect:function(dom_value,json_obj){that.attr("value",results_set[current_hovered_rank].text);},keydelay:300,minlength:3,method:"get",varname:"input_content",params:""},options||{});(function initDOM(){var ul_id=false;var ul_node=document.createElement("ul");var genUniqueId=function(){var result="ul_james_"+Math.round(Math.random()*424242);if(jQuery("#"+result).length>0)
{result=genUniqueId();}
return result;};ul_id=genUniqueId();jQuery(ul_node).attr("id",ul_id).addClass("ul_james");that.after(ul_node);ul_element=jQuery("#"+ul_id);ul_element.hide();})();var initCSS=function initCSS(){var input_offset=that.offset();ul_element.css({top:input_offset.top+that.outerHeight(),width:that.outerWidth(),left:input_offset.left,position:"absolute"});}
that.keydown(function(event){if(event.keyCode===13)
{return false;}});var keyevent_current_timer=false;that.keyup(function(event){var is_specific_action=false;for(var i=0;keyEvents[i];i++)
{if(event.keyCode===keyEvents[i].keycode)
{is_specific_action=true;keyEvents[i].action();break;}}
if(is_specific_action===false)
{if(keyevent_current_timer!==false)
{window.clearTimeout(keyevent_current_timer);keyevent_current_timer=false;}
keyevent_current_timer=window.setTimeout(function(){ajaxUpdate();},o.keydelay);}});var ajaxUpdate=function(){var value_to_send=that.attr("value");if(value_to_send.length>0&&(o.minlength===false||value_to_send.length>=o.minlength))
{$.ajax({type:o.method,data:o.varname+"="+value_to_send+"&"+o.params,url:url_to_call,dataType:"json",success:function(data){var arr=o.onKeystroke(data);results_set=[];current_hovered=0;for(var i in arr)
{if(arr[i]!==null)
{if(typeof(arr[i].json)==="undefined")
{results_set.push({text:arr[i],json:{}});}
else
{results_set.push({text:arr[i].text,json:arr[i].json});}}}
updateDom();}});}
else
{cleanResults();}}
var updateDom=function(){jQuery(ul_element).empty();var is_empty=true;initCSS();for(var i in results_set)
{if(results_set[i]!==null)
{var li_elem=document.createElement("li");jQuery(li_elem).addClass("li_james");if(i==(current_hovered_rank%results_set.length))
{jQuery(li_elem).addClass("li_james_hovered");}
jQuery(li_elem).append(results_set[i].text);jQuery(ul_element).append(li_elem);bind_elem_mouse_hover(li_elem,i);is_empty=false;}}
if(is_empty)
{jQuery(ul_element).hide();}
else
{jQuery(ul_element).show();}}
var bind_elem_mouse_hover=function(elem,i){jQuery(elem).hover(function(){jQuery(ul_element).find(".li_james_hovered").removeClass("li_james_hovered");jQuery(elem).addClass("li_james_hovered");current_hovered_rank=i;},function(){jQuery(elem).removeClass("li_james_hovered");current_hovered_rank=0;});jQuery(elem).click(function(){keyEventEnter();});}
var cleanResults=function(){jQuery(ul_element).empty();jQuery(ul_element).hide();results_set=[];current_hovered_rank=0;}
var keyEventKeyUp=function(){if(current_hovered_rank>0)
{current_hovered_rank--;}
else if(results_set.length)
{current_hovered_rank=results_set.length-1;}
updateDom();}
var keyEventKeyDown=function(){if(current_hovered_rank<(results_set.length-1))
{current_hovered_rank++;}
else
{current_hovered_rank=0;}
updateDom();}
var keyEventEnter=function(){if(results_set.length>0)
{that.attr("value",o.onSelect(results_set[current_hovered_rank].text,results_set[current_hovered_rank].json));}
cleanResults();}
var keyEventEsc=function(){that.attr("value","");cleanResults();}};