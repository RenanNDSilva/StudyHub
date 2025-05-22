const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
})

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
})

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".form-container.sign-in form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const email = form.querySelector('input[type="email"]').value;
        const password = form.querySelector('input[type="password"]').value;

        try {
            const response = await fetch("http://127.0.0.1:8000/users/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert("Erro no login: " + (errorData.detail || "Verifique suas credenciais."));
                return;
            }

            const data = await response.json();
            console.log("Token recebido:", data);

            // Salva o token no localStorage para usar nas próximas requisições
            localStorage.setItem("access_token", data.access_token);

            alert("Login realizado com sucesso!");

            // Redireciona para outra página após login (ajuste conforme seu projeto)
            window.location.href = "index.html";

        } catch (error) {
            console.error("Erro:", error);
            alert("Erro ao conectar com o servidor.");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.querySelector(".form-container.sign-up form");

    registerForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = registerForm.querySelector('input[placeholder="Nome Completo"]').value;
        const email = registerForm.querySelector('input[type="email"]').value;
        const password = registerForm.querySelector('input[type="password"]').value;

        try {
            const response = await fetch("http://127.0.0.1:8000/users/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert("Erro no cadastro: " + (errorData.detail || "Verifique os dados."));
                return;
            }

            const data = await response.json();
            console.log("Usuário criado:", data);

            alert("Cadastro realizado com sucesso!");

            // Após cadastro, redireciona para login ou já faz login automático se quiser
            window.location.href = "login.html";

        } catch (error) {
            console.error("Erro:", error);
            alert("Erro ao conectar com o servidor.");
        }
    });
});