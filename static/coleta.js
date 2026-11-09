const selectProduto = document.getElementById("produto");
const selectMercado = document.getElementById("mercado");
const campoValor = document.getElementById("valor");
const campoData = document.getElementById("data");
const avisoPreco = document.getElementById("aviso-preco");
const avisoCsv = document.getElementById("aviso-csv");

// Data de hoje no formato AAAA-MM-DD (o locale "sv-SE" já devolve nesse formato)
campoData.value = new Date().toLocaleDateString("sv-SE");

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function aviso(elemento, tipo, html) {
  elemento.innerHTML = `<div class="alert alert-${tipo} mb-0">${html}</div>`;
}

async function carregarListas() {
  try {
    const [produtos, mercados] = await Promise.all([
      fetch("/api/produtos").then((r) => r.json()),
      fetch("/api/mercados").then((r) => r.json()),
    ]);
    selectProduto.innerHTML = produtos
      .map(
        (p) =>
          `<option value="${p.id}">${escapar(p.nome)} (${escapar(p.unidade)})</option>`,
      )
      .join("");
    selectMercado.innerHTML = mercados
      .map((m) => `<option value="${m.id}">${escapar(m.nome)}</option>`)
      .join("");
  } catch (erro) {
    console.error(erro);
    aviso(
      avisoPreco,
      "danger",
      "Não foi possível carregar produtos e mercados.",
    );
  }
}

document
  .getElementById("form-preco")
  .addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const corpo = {
      produto_id: Number(selectProduto.value),
      mercado_id: Number(selectMercado.value),
      valor: Number(campoValor.value),
      data_coleta: campoData.value,
    };

    try {
      const resp = await fetch("/api/precos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(corpo),
      });
      if (resp.ok) {
        aviso(avisoPreco, "success", "Preço cadastrado com sucesso.");
        campoValor.value = "";
        campoValor.focus();
      } else {
        const dados = await resp.json();
        const detalhe =
          typeof dados.detail === "string" ? dados.detail : "Dados inválidos.";
        aviso(avisoPreco, "danger", escapar(detalhe));
      }
    } catch (erro) {
      console.error(erro);
      aviso(
        avisoPreco,
        "danger",
        "Não foi possível salvar agora. Tente novamente.",
      );
    }
  });

document
  .getElementById("form-csv")
  .addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const arquivo = document.getElementById("arquivo").files[0];
    if (!arquivo) return;

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    try {
      const resp = await fetch("/api/importar-csv", {
        method: "POST",
        body: formData,
      });
      const dados = await resp.json();

      if (!resp.ok) {
        aviso(avisoCsv, "danger", escapar(dados.detail || "Erro ao importar."));
        return;
      }

      let html = `<strong>${dados.importados}</strong> preço(s) importado(s).`;
      if (dados.erros.length > 0) {
        const itens = dados.erros
          .map((e) => `<li>Linha ${e.linha}: ${escapar(e.motivo)}</li>`)
          .join("");
        html += `<br>${dados.erros.length} linha(s) com erro:<ul class="mb-0">${itens}</ul>`;
      }
      aviso(avisoCsv, dados.erros.length ? "warning" : "success", html);
    } catch (erro) {
      console.error(erro);
      aviso(avisoCsv, "danger", "Não foi possível importar agora.");
    }
  });

carregarListas();
