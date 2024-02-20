function navbar_change(){
    document.getElementById("navbar").position = "static";
}
target = document.getElementById("navbar")
const observer = new IntersectionObserver(navbar_change, { threshold: 1 })
observer.observe(target);
