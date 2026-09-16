let todosOsConcursos = [];

async function carregar() {
  try {
    const resp = await fetch('data/concursos.json');
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

  let filtrados = todosOsConcursos.filter((c) => {
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
  corpo.innerHTML = filtrados.map(linhaHtml).join('');

  document.getElementById('vazio').hidden = filtrados.length > 0;
}

function linhaHtml(c) {
  const dias = c.dias_restantes;
  let classeUrgencia = '';
  if (dias !== null && dias !== undefined) {
    if (dias <= 7) classeUrgencia = 'urgente';
    else if (dias <= 15) classeUrgencia = 'atencao';
  }

  const prazoTexto = c.data_limite
    ? `${c.data_limite}${dias !== null && dias !== undefined ? ` (${dias}d)` : ''}`
    : '—';

  const local = c.localizacao === 'recife_verificar'
    ? 'Recife <span class="selo-verificar">verificar</span>'
    : 'Recife';

  return `<tr class="${classeUrgencia}">
    <td>${escapeHtml(c.cargo)}</td>
    <td>${escapeHtml(c.orgao)}</td>
    <td>${escapeHtml(prazoTexto)}</td>
    <td>${local}</td>
    <td><a href="${escapeHtml(c.link)}" target="_blank" rel="noopener noreferrer">Ver edital</a></td>
  </tr>`;
}

document.getElementById('busca').addEventListener('input', renderizar);

carregar();
