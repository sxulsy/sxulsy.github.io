// 导航栏滚动效果
window.addEventListener('scroll', function () {
    const heroSection = document.querySelector('.hero-section');
    const heroSpacer = document.querySelector('.hero-spacer');
    if (heroSection && heroSpacer) {
        if (window.scrollY > 1) {
            heroSection.classList.add('scrolled');
            heroSpacer.classList.add('scrolled');
        } else {
            heroSection.classList.remove('scrolled');
            heroSpacer.classList.remove('scrolled');
        }
    }
});


// 移动端导航切换
const navbarToggle = document.querySelector('.navbar-toggle');
const navbarMenu = document.querySelector('.navbar-menu');

navbarToggle.addEventListener('click', function() {
    navbarMenu.classList.toggle('active');
});

// 点击导航链接后关闭移动端菜单
const navbarLinks = document.querySelectorAll('.navbar-menu a');
navbarLinks.forEach(link => {
    link.addEventListener('click', function() {
        navbarMenu.classList.remove('active');
    });
});

// 顶部轮播图效果
let currentSlide = 0;
const slides = document.querySelectorAll('.hero-slide');
const totalSlides = slides.length;

function showSlide(index) {
    // 移除所有幻灯片的active类
    slides.forEach(slide => {
        slide.classList.remove('active');
    });
    // 添加当前幻灯片的active类
    slides[index].classList.add('active');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
}

// 自动轮播，设置为3秒切换一次
let slideInterval = setInterval(nextSlide, 2500);

// 鼠标悬停时暂停轮播
/*const heroSection = document.querySelector('.hero-section');
if (heroSection) {
    heroSection.addEventListener('mouseenter', function() {
        clearInterval(slideInterval);
    });

    heroSection.addEventListener('mouseleave', function() {
        slideInterval = setInterval(nextSlide, 2500);
    });
}*/

// 平滑滚动到页面顶部
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// 监听页面加载完成事件
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    // 初始化轮播图
    showSlide(currentSlide);
});

// 表单提交处理（如果有表单）
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // 获取表单数据
        const formData = new FormData(this);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message'),
            timestamp: new Date().toISOString()
        };
        
        // 保存到localStorage
        let submissions = JSON.parse(localStorage.getItem('contactSubmissions')) || [];
        submissions.push(data);
        localStorage.setItem('contactSubmissions', JSON.stringify(submissions));
        
        // 显示成功消息
        alert('消息发送成功！');
        
        // 重置表单
        this.reset();
        
        console.log('表单提交成功，数据已保存到localStorage');
    });
});

// 图片懒加载
const lazyImages = document.querySelectorAll('img[data-src]');

if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;
                image.src = image.dataset.src;
                image.removeAttribute('data-src');
                imageObserver.unobserve(image);
            }
        });
    });

    lazyImages.forEach(image => {
        imageObserver.observe(image);
    });
}