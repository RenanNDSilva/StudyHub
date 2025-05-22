document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("novaPostagem");
  const input = document.getElementById("postInput");
  const fileInput = document.getElementById("uploadArquivo");
  const previewContainer = document.getElementById("imagemPreviewContainer");
  const feed = document.getElementById("feedPosts");

  const picker = new EmojiButton({ theme: 'dark' }); // EmojiButton integrado

  let imagensSelecionadas = [];

  function formatarHora() {
    const agora = new Date();
    return agora.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  fileInput.addEventListener("change", function () {
    const files = Array.from(fileInput.files);
    previewContainer.innerHTML = "";
    imagensSelecionadas = [];

    files.forEach((file) => {
      if (!file.type.startsWith("image/")) return;

      const reader = new FileReader();
      reader.onload = function (e) {
        const src = e.target.result;
        imagensSelecionadas.push(src);

        const wrapper = document.createElement("div");
        wrapper.className = "position-relative d-inline-block me-2 mb-2";

        const img = document.createElement("img");
        img.src = src;
        img.className = "img-fluid rounded postagem-img";
        img.style.maxHeight = "200px";
        img.style.width = "auto";

        const closeBtn = document.createElement("button");
        closeBtn.innerHTML = "&times;";
        closeBtn.className = "btn btn-sm btn-danger position-absolute top-0 end-0";
        closeBtn.style.zIndex = "10";
        closeBtn.style.padding = "2px 6px";
        closeBtn.style.fontSize = "0.9rem";
        closeBtn.style.lineHeight = "1";
        closeBtn.style.borderRadius = "50%";

        closeBtn.onclick = function () {
          wrapper.remove();
          imagensSelecionadas = imagensSelecionadas.filter(imgSrc => imgSrc !== src);
        };

        wrapper.appendChild(img);
        wrapper.appendChild(closeBtn);
        previewContainer.appendChild(wrapper);
      };

      reader.readAsDataURL(file);
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const texto = input.value.trim();
    if (texto === "") return;

    const novoPost = document.createElement("div");
    novoPost.className = "card mb-3 bg-dark text-light border-0";

    const conteudo = document.createElement("div");
    conteudo.className = "card-body pb-1";

    conteudo.innerHTML = `
      <div class="d-flex align-items-center mb-2">
        <img src="assets/img/perfil.jpg" alt="Perfil" class="rounded-circle me-2" width="40" height="40">
        <div class="post-usuario">
          Você <small class="text-muted">· ${formatarHora()}</small>
        </div>
      </div>
    `;

    const textoElemento = document.createElement("p");
    textoElemento.className = "mb-2";
    textoElemento.textContent = texto;
    conteudo.appendChild(textoElemento);

    if (imagensSelecionadas.length > 0) {
      imagensSelecionadas.forEach(src => {
        const img = document.createElement("img");
        img.src = src;
        img.className = "img-fluid rounded postagem-img mb-2";
        conteudo.appendChild(img);
      });
    }

    const acoes = document.createElement("div");
    acoes.className = "mt-3 d-flex justify-content-around post-actions";
    acoes.innerHTML = `
      <span class="btn-comentar"><i class="bi bi-chat"></i> 0</span>
      <span class="btn-curtir"><i class="bi bi-heart"></i> 0</span>
      <span class="btn-compartilhar"><i class="bi bi-share"></i></span>
    `;
    conteudo.appendChild(acoes);

    const comentarioWrapper = document.createElement("div");
    comentarioWrapper.className = "mt-3 comentarios-area";

    comentarioWrapper.innerHTML = `
      <div class="input-group">
        <input type="text" class="form-control form-control-sm comentario-input bg-dark text-light border-secondary"
        placeholder="Adicione um comentário...">
        <span class="input-group-text bg-dark border-secondary text-muted emoji-btn"><i class="bi bi-emoji-smile"></i></span>
      </div>
      <ul class="list-unstyled comentarios-list mt-2"></ul>
    `;
    conteudo.appendChild(comentarioWrapper);
    novoPost.appendChild(conteudo);
    feed.prepend(novoPost);

    // Ativa picker de emoji nesse post
    const trigger = comentarioWrapper.querySelector(".emoji-btn");
    const inputComentario = comentarioWrapper.querySelector(".comentario-input");
    trigger.addEventListener("click", () => {
      picker.togglePicker(trigger);
    });
    picker.on('emoji', emoji => {
      const cursor = inputComentario.selectionStart;
      const texto = inputComentario.value;
      inputComentario.value = texto.slice(0, cursor) + emoji + texto.slice(cursor);
      inputComentario.focus();
      inputComentario.setSelectionRange(cursor + emoji.length, cursor + emoji.length);
    });

    // Reset
    input.value = "";
    fileInput.value = "";
    previewContainer.innerHTML = "";
    imagensSelecionadas = [];
  });

  document.body.addEventListener("click", function (e) {
    if (e.target.tagName === "IMG" && e.target.classList.contains("postagem-img")) {
      const modalImg = document.getElementById("imagemExpandida");
      modalImg.src = e.target.src;
      const modal = new bootstrap.Modal(document.getElementById("modalImagemExpandida"));
      modal.show();
    }
  });

  feed.addEventListener("click", function (e) {
    const target = e.target;

    if (target.closest(".btn-curtir")) {
      const span = target.closest("span");
      const icon = span.querySelector("i");
      let texto = span.textContent.trim();
      let count = parseInt(texto) || 0;

      const isLiked = icon.classList.contains("bi-heart-fill");

      if (isLiked) {
        // Descurtir
        count = Math.max(0, count - 1);
        icon.classList.remove("bi-heart-fill", "text-danger");
        icon.classList.add("bi-heart");
      } else {
        // Curtir
        count++;
        icon.classList.remove("bi-heart");
        icon.classList.add("bi-heart-fill", "text-danger");
      }

      span.innerHTML = `<i class="${icon.className}"></i> ${count}`;
    }

    if (target.closest(".btn-compartilhar")) {
      navigator.clipboard.writeText(window.location.href).then(() => {
        alert("Link copiado para a área de transferência!");
      });
    }

    if (target.closest(".btn-comentar")) {
      const post = target.closest(".card-body");
      const comentariosArea = post.querySelector(".comentarios-area");
      comentariosArea.querySelector(".comentario-input").focus();
    }
  });

  feed.addEventListener("keydown", function (e) {
    if (e.target.classList.contains("comentario-input") && e.key === "Enter") {
      const ul = e.target.closest(".comentarios-area").querySelector(".comentarios-list");
      const valor = e.target.value.trim();
      if (valor !== "") {
        const li = document.createElement("li");
        li.innerHTML = `<strong>Você:</strong> ${valor}`;
        ul.appendChild(li);
        e.target.value = "";

        const post = e.target.closest(".card-body");
        const contador = post.querySelector(".btn-comentar");
        let qtd = parseInt(contador.textContent.trim()) || 0;
        qtd++;
        contador.innerHTML = `<i class="bi bi-chat"></i> ${qtd}`;
      }
    }
  });
});

document.addEventListener("DOMContentLoaded", async function () {
  const aside = document.getElementById("mini-profile");
  const token = localStorage.getItem("access_token");

  if (!token) {
    if (aside) aside.style.display = "none";
    return;
  }


  try {
    // Decodifica o token JWT para pegar o email (sub)
    const payloadBase64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(decodeURIComponent(escape(atob(payloadBase64))));
    const userEmail = payload.sub;

    // Primeiro busca o user_id via email
    const responseId = await fetch(`http://127.0.0.1:8000/users/get-user-id/${userEmail}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!responseId.ok) {
      if (aside) aside.style.display = "none";
      return;
    }

    const userData = await responseId.json();
    const userId = userData.id;

    // Agora busca os dados do mini user
    const responseUser = await fetch(`http://127.0.0.1:8000/users/get-mini-user/${userId}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!responseUser.ok) {
      if (aside) aside.style.display = "none";
      return;
    }

    const user = await responseUser.json();

    console.log(user)
    // Preencher os dados no HTML
    const img = aside.querySelector("img");
    const strong = aside.querySelector("strong");
    const small = aside.querySelector("small");

    img.src = "http://127.0.0.1:8000/src/media/uploads/photo_profile/" + user.photo_profile || "generic_photo";
    strong.textContent = user.name || "Usuário";
    small.textContent = user.email || "";

  } catch (error) {
    console.error("Erro ao carregar dados do usuário:", error);
    if (aside) aside.style.display = "none";
  }
});