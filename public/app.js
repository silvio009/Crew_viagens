/**
 * 1. CONFIGURAÇÃO E ESTILOS
 */
const configScript = document.createElement('script');
configScript.src = '/public/config.js?t=' + Date.now();
document.head.appendChild(configScript);

const style = document.createElement('style');
style.textContent = `
    @keyframes spin-viagem {
        to { transform: rotate(360deg); }
    }

    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    div[role="article"]:has(.loader-wrapper) {
        display: flex !important;
        justify-content: flex-start !important;
        padding: 0 !important;
        margin: 0 !important;
        text-indent: 0 !important;
        line-height: normal !important;
    }
`;
document.head.appendChild(style);

/**
 * 2. SPINNER
 */
function injetarSpinner() {
    const observer = new MutationObserver(() => {
        const mensagens = document.querySelectorAll('.prose div[role="article"]');
        mensagens.forEach((el) => {
            if (
                el.textContent.includes('Pesquisando e gerando seu roteiro') &&
                !el.querySelector('.spinner-viagem')
            ) {
                const texto = el.textContent.trim();
                el.innerHTML = `
                    <span class="loader-wrapper">
                        <span class="loader-shimmer">${texto}</span>
                        <span class="spinner-viagem"></span>
                    </span>
                `;
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

/**
 * 3. FUNÇÕES DE DATA
 */
function parseDateBR(str) {
    // Aceita DD/MM/YYYY
    const parts = str.trim().split('/');
    if (parts.length !== 3) return null;
    return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
}

function gerarListaDias(dataIda, dataVolta) {
    const dias = [];
    const atual = new Date(dataIda);
    while (atual <= dataVolta) {
        dias.push(new Date(atual));
        atual.setDate(atual.getDate() + 1);
    }
    return dias;
}

function formatarDia(date) {
    return date.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' });
}

/**
 * 4. BUSCA DE CLIMA
 */
async function buscarPrevisao(cidade) {
    let apiKey = window._owKey;
    if (!apiKey) {
        await new Promise(r => setTimeout(r, 1500));
        apiKey = window._owKey;
    }
    if (!apiKey) return null;

    try {
        const url = `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(cidade)}&appid=${apiKey}&units=metric&lang=pt_br`;
        const res = await fetch(url);
        const data = await res.json();
        if (!data.list) return null;
        return data;
    } catch (e) {
        console.error(e);
        return null;
    }
}

async function buscarClimaAtual(cidade) {
    let apiKey = window._owKey;
    if (!apiKey) {
        await new Promise(r => setTimeout(r, 1500));
        apiKey = window._owKey;
    }
    if (!apiKey) return null;

    try {
        const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(cidade)}&appid=${apiKey}&units=metric&lang=pt_br`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.cod !== 200) return null;
        return data;
    } catch (e) {
        return null;
    }
}

/**
 * 5. MONTA OS DIAS DO PERÍODO
 * Para datas dentro dos 5 dias: usa previsão real
 * Para datas fora dos 5 dias: replica padrão da semana atual
 */
async function montarClimasPeriodo(cidade, dataIda, dataVolta) {
    const diasPeriodo = gerarListaDias(dataIda, dataVolta);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const limite5dias = new Date(hoje);
    limite5dias.setDate(hoje.getDate() + 5);

    const previsao = await buscarPrevisao(cidade);
    const atual = await buscarClimaAtual(cidade);

    // Mapa de previsões reais por data YYYY-MM-DD
    const mapaPrevisao = {};
    if (previsao && previsao.list) {
        previsao.list.forEach(item => {
            const d = new Date(item.dt * 1000);
            const chave = d.toISOString().slice(0, 10);
            if (!mapaPrevisao[chave]) {
                mapaPrevisao[chave] = {
                    temp: Math.round(item.main.temp),
                    icone: item.weather[0].icon,
                    descricao: item.weather[0].description
                };
            }
        });
    }

    // Padrão da semana atual para replicar
    const padraoDiaSemana = {};
    if (previsao && previsao.list) {
        previsao.list.forEach(item => {
            const d = new Date(item.dt * 1000);
            const diaSemana = d.getDay(); // 0=dom, 1=seg...
            if (!padraoDiaSemana[diaSemana]) {
                padraoDiaSemana[diaSemana] = {
                    temp: Math.round(item.main.temp),
                    icone: item.weather[0].icon,
                    descricao: item.weather[0].description
                };
            }
        });
    }

    // Fallback: clima atual
    const fallback = atual ? {
        temp: Math.round(atual.main.temp),
        icone: atual.weather[0].icon,
        descricao: atual.weather[0].description
    } : { temp: '--', icone: '01d', descricao: 'N/A' };

    return diasPeriodo.map(dia => {
        const chave = dia.toISOString().slice(0, 10);
        const diaSemana = dia.getDay();

        let clima;
        if (mapaPrevisao[chave]) {
            clima = mapaPrevisao[chave];
        } else if (padraoDiaSemana[diaSemana]) {
            clima = { ...padraoDiaSemana[diaSemana], replicado: true };
        } else {
            clima = { ...fallback, replicado: true };
        }

        return {
            label: formatarDia(dia),
            ...clima
        };
    });
}

/**
 * 6. ATUALIZA A TABELA COM OS DADOS
 */
async function atualizarClimaTabela(cidade, dataIda, dataVolta) {
    const container = document.querySelector('.tabela-destinos');
    if (!container) return;

    container.innerHTML = `<div style="color:#555; font-size:0.75rem; text-align:center; padding:20px;">Buscando clima...</div>`;

    const climas = await montarClimasPeriodo(cidade, dataIda, dataVolta);

    if (!climas || climas.length === 0) {
        container.innerHTML = `<div style="color:#ff6b6b; font-size:0.75rem; text-align:center; padding:20px;">Clima não encontrado.</div>`;
        return;
    }

    const diasHTML = climas.map(d => `
        <div style="display:flex; flex-direction:column; align-items:center; gap:2px; min-width:52px;">
            <div style="font-size:0.62rem; color:#666;">${d.label}</div>
            <img src="https://openweathermap.org/img/wn/${d.icone}.png" style="width:28px;height:28px;"/>
            <div style="font-size:0.78rem; color:#ccc; font-weight:600;">${d.temp}°</div>
            ${d.replicado ? '<div style="font-size:0.55rem; color:#444;">~est.</div>' : ''}
        </div>
    `).join('');

    container.innerHTML = `
        <div style="font-size:0.62rem; color:#555; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">
            🌤 ${cidade} — ${climas[0].label.split(',')[1]?.trim() || ''} → ${climas[climas.length-1].label.split(',')[1]?.trim() || ''}
        </div>
        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center;">
            ${diasHTML}
        </div>
        <div style="font-size:0.55rem; color:#444; margin-top:6px; text-align:center;">~est. = estimativa baseada no padrão atual</div>
    `;
}

/**
 * 7. BOAS-VINDAS
 */
function injetarBoasVindas() {
    if (document.querySelector('.boas-vindas')) return;

    const welcomeScreen = document.querySelector('#welcome-screen');
    const input = document.querySelector('#message-composer');

    if (welcomeScreen && input) {
        const div = document.createElement('div');
        div.className = 'boas-vindas';
        div.style.cssText = "text-align:center; padding:0 16px 12px;";
        div.innerHTML = `
            <p style="font-size:1.1rem; color:#aaaaaa; margin:0 0 4px;">Olá, viajante!</p>
            <p style="font-size:0.85rem; color:#666; margin:0;">Digite sua cidade de origem para começar.</p>
        `;
        welcomeScreen.insertBefore(div, input);
    }
}

/**
 * 8. WIDGET CLIMA (INICIAL)
 */
function injetarTabelaClima() {
    if (document.querySelector('.tabela-destinos')) return;

    const div = document.createElement('div');
    div.className = 'tabela-destinos';
    div.innerHTML = `<div style="color:#444; font-size:0.75rem; text-align:center;">🌤 Clima aparecerá após informar o destino e as datas.</div>`;
    document.body.appendChild(div);
}

/**
 * 9. OBSERVAR CHAT — destino e datas
 */
let aguardandoDestino = false;
let aguardandoDataIda = false;
let aguardandoDataVolta = false;
let destinoAtual = '';
let dataIdaAtual = '';
let observerIniciado = false;

function observarDestino() {
    if (observerIniciado) return;
    observerIniciado = true;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (!(node instanceof HTMLElement)) return;

                const artigos = node.matches?.('[role="article"]')
                    ? [node]
                    : node.querySelectorAll?.('[role="article"]') || [];

                artigos.forEach((artigo) => {
                    const texto = artigo.innerText.trim();
                    if (!texto) return;

                    // Bot perguntou destino
                    if (texto.includes('Qual é o destino da sua viagem')) {
                        aguardandoDestino = true;
                        return;
                    }

                    // Bot perguntou data de ida
                    if (texto.includes('data de partida')) {
                        aguardandoDataIda = true;
                        return;
                    }

                    // Bot perguntou data de volta
                    if (texto.includes('data de volta')) {
                        aguardandoDataVolta = true;
                        return;
                    }

                    // Ignora rodapé do Chainlit
                    if (texto.includes('LLMs podem cometer erros')) return;

                    // Captura destino
                    if (aguardandoDestino && texto.length <= 40) {
                        destinoAtual = texto;
                        aguardandoDestino = false;
                        return;
                    }

                    // Captura data de ida
                    if (aguardandoDataIda && /\d{2}\/\d{2}\/\d{4}/.test(texto)) {
                        dataIdaAtual = texto;
                        aguardandoDataIda = false;
                        return;
                    }

                    // Captura data de volta e dispara busca
                    if (aguardandoDataVolta && /\d{2}\/\d{2}\/\d{4}/.test(texto)) {
                        const dataVoltaAtual = texto;
                        aguardandoDataVolta = false;

                        const ida = parseDateBR(dataIdaAtual);
                        const volta = parseDateBR(dataVoltaAtual);

                        if (ida && volta && destinoAtual) {
                            atualizarClimaTabela(destinoAtual, ida, volta);
                        }
                        return;
                    }
                });
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

/**
 * 10. INICIALIZAÇÃO
 */
const observerGeral = new MutationObserver(() => {
    const welcomeScreen = document.querySelector('#welcome-screen');
    if (welcomeScreen) {
        injetarBoasVindas();
        injetarTabelaClima();
        observarDestino();
        injetarSpinner();
    }
});

observerGeral.observe(document.body, { childList: true, subtree: true });


// Retirando o logo da tela de login 
function removeChainlitLoginLogo() {
    const logos = document.querySelectorAll("img.logo");
    logos.forEach(logo => {
        // Remove somente se for o logo padrão do Chainlit
        if (logo.src.includes("/logo?theme=")) {
            logo.remove();
        }
    });
}

// Remove qualquer logo já existente
removeChainlitLoginLogo();

// Observa a página e remove o logo do Chainlit caso seja recriado dinamicamente
const observer = new MutationObserver(removeChainlitLoginLogo);
observer.observe(document.body, { childList: true, subtree: true });


// alterando o texto da tala de entrada do login
function atualizarH1() {
    const h1Span = document.querySelector('h1.text-2xl.font-bold span');
    if (h1Span) {
        h1Span.textContent = "Faça login para organizar sua próxima experiência de viagem";
        clearInterval(intervalo); 
    }
}
function alterarLabelEmail() {
    const spanEmail = document.querySelector('label[for="email"] span');
    
    if (spanEmail) {
        spanEmail.textContent = "Usuário";
        clearInterval(intervaloEmail);
    }
}


function alterarPlaceholderEmail() {
    const inputEmail = document.querySelector('input#email');

    if (inputEmail) {
        inputEmail.placeholder = "";
        clearInterval(intervaloPlaceholder);
    }
}

const intervalo = setInterval(atualizarH1, 100);
const intervaloEmail = setInterval(alterarLabelEmail, 100);
const intervaloPlaceholder = setInterval(alterarPlaceholderEmail, 100);

function adicionarLinkCriarConta() {
    const form = document.querySelector("form");
    
    if (form && !document.querySelector("#link-criar-conta")) {
        const p = document.createElement("p");
        p.id = "link-criar-conta";
        p.style.textAlign = "center";
        p.style.fontSize = "14px";

        p.innerHTML = `
            Não possui conta? 
            <a href="http://localhost:8001/registro" target="_blank" style="
                color: #d4d803;
                text-decoration: none;
                font-weight: 500;
            ">
                Criar conta
            </a>
        `;

        form.appendChild(p);
    }
}

const intervaloLink = setInterval(() => {
    if (document.querySelector("form")) {
        adicionarLinkCriarConta();
        clearInterval(intervaloLink);
    }
}, 100);


// Fica observando o DOM até o botão aparecer
const observer_button = new MutationObserver(() => {
    // Tenta encontrar o link/botão de "criar conta" do Chainlit
    const links = document.querySelectorAll('a, button');
    
    links.forEach(el => {
        const texto = el.textContent.trim().toLowerCase();
        if (
            texto.includes('criar conta') || 
            texto.includes('sign up') || 
            texto.includes('register') ||
            texto.includes('registrar')
        ) {
            el.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                window.open('http://localhost:8001/registro', '_blank');
            };
        }
    });
});

observer_button.observe(document.body, {
    childList: true,
    subtree: true
});
