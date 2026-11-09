const form = document.getElementById("form-busca");
const campo = document.getElementById("campo-busca");
const resultado = document.getElementById("resultado");

const moeda = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

// "2026-11-09" -> "09/11/2026" (sem usar Date, para evitar problema de fuso horário)
function formatarData(iso) {
  const [ano, mes, dia] = iso.split("-");
  return `${dia}/${mes}/${ano}`;
}

// Evita que texto vindo do banco ou digitado seja interpretado como HTML
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function mostrarAviso(tipo, mensagem) {
  resultado.innerHTML = `
    <div class="col-12 col-md-8 col-lg-6">
      <div class="alert alert-${tipo} text-center">${mensagem}</div>
    </div>`;
}

function montarCard(item) {
  const barato = item.mais_barato;

  const outros = item.precos
    .slice(1)
    .map((p) => {
      const diferenca = p.valor - barato.valor;
      return `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>${escapar(p.mercado)}</strong><br>
          <small class="text-muted">${escapar(p.bairro || "")} · atualizado em ${formatarData(p.data_coleta)}</small>
        </div>
        <div class="text-end">
          <span class="fw-semibold">${moeda.format(p.valor)}</span><br>
          <small class="text-danger">+ ${moeda.format(diferenca)}</small>
        </div>
      </li>`;
    })
    .join("");

  return `
    <div class="col-12 col-md-8 col-lg-6">
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-white">
          <h2 class="h5 mb-0">${escapar(item.produto)}
            <small class="text-muted">(preço por ${escapar(item.unidade)})</small>
          </h2>
        </div>

        <div class="destaque p-3 text-center">
          <span class="badge bg-success mb-2">Mais barato</span>
          <div class="preco-destaque">${moeda.format(barato.valor)}</div>
          <div class="fw-semibold">${escapar(barato.mercado)}</div>
          <small class="text-muted">${escapar(barato.bairro || "")} · atualizado em ${formatarData(barato.data_coleta)}</small>
        </div>

        <ul class="list-group list-group-flush">${outros}</ul>
      </div>
    </div>`;
}

async function buscar(texto) {
  mostrarAviso("secondary", "Buscando...");
  try {
    const resp = await fetch(`/api/buscar?q=${encodeURIComponent(texto)}`);
    if (!resp.ok) throw new Error(`Erro ${resp.status}`);
    const dados = await resp.json();

    if (dados.total === 0) {
      mostrarAviso(
        "warning",
        `Nenhum perecível encontrado para <strong>${escapar(texto)}</strong>.`,
      );
      return;
    }
    resultado.innerHTML = dados.resultados.map(montarCard).join("");
  } catch (erro) {
    console.error(erro);
    mostrarAviso("danger", "Não foi possível buscar agora. Tente novamente.");
  }
}

form.addEventListener("submit", (evento) => {
  evento.preventDefault(); // impede o recarregamento da página
  const texto = campo.value.trim();
  if (texto) buscar(texto);
});
