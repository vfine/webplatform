function foo(tag,data,pm) {
   /* ---------------------  My Entry point ---------------------- */   
   var thisTag = $(tag);
   thisTag.empty();
   console.log("Enter the user function:" + this + " pm=" + pm);

   var txt='Test text:';
   for(var key in data)
     {
       txt=txt+key+':'+ data[key]+';<br/>';
     };
   
   $(tag).html(txt);
}
