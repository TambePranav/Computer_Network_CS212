let cnt=0;
document.getElementById("mybutton").onclick=function()
{
   if(cnt==1){
    document.getElementById("myimage").src='image1.jpeg';
    cnt=0;
   } 
   else { document.getElementById("myimage").src='image2.jpeg';
cnt=1;}
}
 