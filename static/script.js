fetch("/api/teste")
  .then((res) => res.json())
  .then((dados) => {
    document.getElementById("status").textContent = dados.mensagem;
  });
