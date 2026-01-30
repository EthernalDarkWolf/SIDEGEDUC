// UI animations for sidebar and small interactions
(function(){
    // gentle submenu open animation using class toggles
    document.querySelectorAll('.has-children > .side-btn').forEach(function(btn){
        btn.addEventListener('mouseenter', function(){
            btn.style.transform = 'translateY(-4px)';
            btn.style.transition = 'transform .18s ease';
        });
        btn.addEventListener('mouseleave', function(){
            btn.style.transform = '';
        });
    });

    // highlight current menu slowly
    document.querySelectorAll('.side-sub li a').forEach(function(a){
        a.addEventListener('mouseover', function(){
            a.style.background = 'rgba(255,255,255,0.04)';
            a.style.transition = 'background .18s ease';
        });
        a.addEventListener('mouseout', function(){
            a.style.background = '';
        });
    });

    // small entrance animation for content cards
    window.addEventListener('load', function(){
        document.querySelectorAll('.card').forEach(function(c, i){
            c.style.opacity = 0;
            c.style.transform = 'translateY(12px)';
            setTimeout(function(){ c.style.transition = 'opacity .4s ease, transform .4s cubic-bezier(.2,.9,.2,1)'; c.style.opacity = 1; c.style.transform = ''; }, 120 + i*80);
        });
    });
})();
