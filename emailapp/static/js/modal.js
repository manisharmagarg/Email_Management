$(document).ready(function(){
 $(".deletebutton").click(function(){
   var value = $(this).attr("data-href");
   $("#hiddentext").val(value);
 });

 $("#modalButton").click(function(){
  var url=$("#hiddentext").val();
  window.location.href=url;
 })
});