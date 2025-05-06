const container = document.getElementById('container');
const registerBtn = document.getElementById('add');
const loginBtn = document.getElementById('search');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});