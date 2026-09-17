/* Living Archive · Archiv-Kompass (la.js)
   Injiziert auf jeder Seite denselben Navigations-Kompass.
   Sektionen = Register der einen Sprache. */
(function(){
  var SECTIONS=[
    {id:"portal",      label:"Portal · Das Lebendige Archiv", href:"/",                    dot:"#b8742a"},
    {id:"notizen",     label:"Notizen-Atlas · 315 Notizen",   href:"/notizen/",            dot:"#b39c4f"},
    {id:"garten",      label:"Traumwald · interaktiv",        href:"/garten/",             dot:"#064013"},
    {id:"brouillon",   label:"Brouillon-Browser · Novalis",   href:"/quellen/brouillon/",  dot:"#5D80D9"},
    {id:"studien",     label:"Studie · Enzyklopädistik",      href:"/studien/novalis-enzyklopaedistik/", dot:"#5b6aa8"},
    {id:"methodik",    label:"Methodik · 7 Arbeitsweisen",    href:"/methodik/",           dot:"#1f6f6b"},
    {id:"expeditionen",label:"Expeditionen · Chat-Projekte",  href:"/expeditionen/",       dot:"#b8742a"}
  ];
  var here=(document.body.getAttribute("data-section")||"");
  var root=document.createElement("div");
  root.className="la-kompass";
  var menu='<div class="la-k-menu"><div class="la-k-cap">Archiv-Kompass</div>';
  SECTIONS.forEach(function(s){
    menu+='<a href="'+s.href+'" class="'+(s.id===here?"here":"")+'"><span class="la-k-dot" style="--dot:'+s.dot+'"></span>'+s.label+'</a>';
  });
  menu+='</div>';
  root.innerHTML='<button class="la-k-trigger" aria-label="Archiv-Kompass" title="Archiv-Kompass">✳</button>'+menu;
  document.body.appendChild(root);
  var btn=root.querySelector(".la-k-trigger");
  btn.addEventListener("click",function(e){ e.stopPropagation(); root.classList.toggle("open"); });
  document.addEventListener("click",function(){ root.classList.remove("open"); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape") root.classList.remove("open"); });
})();
