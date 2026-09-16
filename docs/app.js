let todosOsConcursos = [];

const CHAVE_DECISOES = 'concursos_decisoes_v1';

function carregarDecisoes() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE_DECISOES)) || {};
  } catch (erro) {
    return {};
  }
}

function salvarDecisao(id, decisao) {
  try {
    const decisoes = carregarDecisoes();
    if (decisao === null) {
      delete decisoes[id];
    } else {
      decisoes[id] = decisao;
    }
    localStorage.setItem(CHAVE_DECISOES, JSON.stringify(decisoes));
  } catch (erro) {
    console.error('Não foi possível salvar sua decisão neste navegador.', erro);
  }
}

async function carregar() {
  try {
    const resp = await fetch('data/concursos.json', { cache: 'no-store' });
    const dados = await resp.json();
    todosOsConcursos = dados.concursos || [];
    document.getElementById('atualizado').textContent = dados.atualizado_em
      ? `Atualizado em ${formatarDataHora(dados.atualizado_em)}`
      : 'Ainda sem dados — rode o robô ao menos uma vez.';
    renderizar();
  } catch (erro) {
    document.getElementById('atualizado').textContent = 'Não foi possível carregar os dados.';
    console.error(erro);
  }
}

function formatarDataHora(iso) {
  const d = new Date(iso);
  return d.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}

function escapeHtml(texto) {
  const div = document.createElement('div');
  div.textContent = texto ?? '';
  return div.innerHTML;
}

function renderizar() {
  const termo = document.getElementById('busca').value.toLowerCase();
  const decisoes = carregarDecisoes();

  let filtrados = todosOsConcursos.filter((c) => {
    if (decisoes[c.id] === 'descartar') return false;
    const textoBusca = `${c.cargo} ${c.orgao} ${c.titulo_bruto}`.toLowerCase();
    return !termo || textoBusca.includes(termo);
  });

  filtrados.sort((a, b) => {
    const da = a.dias_restantes;
    const db = b.dias_restantes;
    if (da == null) return 1;
    if (db == null) return -1;
    return da - db;
  });

  const corpo = document.getElementById('corpoTabela');
  corpo.innerHTML = filtrados.map((c) => linhaHtml(c, decisoes[c.id])).join('');

  document.getElementById('vazio').hidden = filtrados.length > 0;
}

function linhaHtml(c, decisao) {
  const dias = c.dias_restantes;
  let classeUrgencia = '';
  if (dias !== null && dias !== undefined) {
    if (dias <= 7) classeUrgencia = 'urgente';
    else if (dias <= 15) classeUrgencia = 'atencao';
  }

  const prazoTexto = c.data_limite
    ? `${c.data_limite}${dias !== null && dias !== undefined ? ` (${dias}d)` : ''}`
    : '—';

  let local = 'Recife';
  if (c.localizacao === 'recife_verificar') {
    if (decisao === 'manter') {
      local = 'Recife <span class="selo-verificar selo-confirmado">confirmado por você</span> '
        + `<button class="botao-decisao" data-id="${c.id}" data-acao="desfazer">desfazer</button>`;
    } else {
      local = 'Recife <span class="selo-verificar">verificar</span>'
        + `<div class="botoes-decisao">`
        + `<button class="botao-decisao" data-id="${c.id}" data-acao="manter">É em Recife</button>`
        + `<button class="botao-decisao" data-id="${c.id}" data-acao="descartar">Não é</button>`
        + `</div>`;
    }
  }

  return `<tr class="${classeUrgencia}">
    <td>${escapeHtml(c.cargo)}</td>
    <td>${escapeHtml(c.orgao)}</td>
    <td>${escapeHtml(prazoTexto)}</td>
    <td>${local}</td>
    <td><a href="${escapeHtml(c.link)}" target="_blank" rel="noopener noreferrer">Ver edital</a></td>
  </tr>`;
}

document.getElementById('busca').addEventListener('input', renderizar);

document.getElementById('corpoTabela').addEventListener('click', (evento) => {
  const botao = evento.target.closest('.botao-decisao');
  if (!botao) return;

  const id = Number(botao.dataset.id);
  const acao = botao.dataset.acao;

  if (acao === 'desfazer') {
    salvarDecisao(id, null);
  } else {
    salvarDecisao(id, acao);
  }
  renderizar();
});

carregar();
