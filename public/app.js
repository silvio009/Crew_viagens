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

/* SPINNER */
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

/* FUNÇÕES DE DATA */
function parseDateBR(str) {
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

/* BUSCA DE CLIMA */
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

/* MONTA OS DIAS DO PERÍODO */
async function montarClimasPeriodo(cidade, dataIda, dataVolta) {
    const diasPeriodo = gerarListaDias(dataIda, dataVolta);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const limite5dias = new Date(hoje);
    limite5dias.setDate(hoje.getDate() + 5);

    const previsao = await buscarPrevisao(cidade);
    const atual = await buscarClimaAtual(cidade);

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

    const padraoDiaSemana = {};
    if (previsao && previsao.list) {
        previsao.list.forEach(item => {
            const d = new Date(item.dt * 1000);
            const diaSemana = d.getDay();
            if (!padraoDiaSemana[diaSemana]) {
                padraoDiaSemana[diaSemana] = {
                    temp: Math.round(item.main.temp),
                    icone: item.weather[0].icon,
                    descricao: item.weather[0].description
                };
            }
        });
    }

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

/* ATUALIZA A TABELA COM OS DADOS */
async function atualizarClimaTabela(cidade, dataIda, dataVolta) {
    const container = document.querySelector('.tabela-destinos');
    if (!container) return;

    container.innerHTML = `<div style="color:#555;font-size:0.75rem;text-align:center;padding:20px;">Buscando clima...</div>`;

    const climas = await montarClimasPeriodo(cidade, dataIda, dataVolta);

    if (!climas || climas.length === 0) {
        container.innerHTML = `<div style="color:#ff6b6b;font-size:0.75rem;text-align:center;padding:20px;">Clima não encontrado.</div>`;
        return;
    }

    const primeiroDia = climas[0].label.split(',')[1]?.trim() || '';
    const ultimoDia = climas[climas.length - 1].label.split(',')[1]?.trim() || '';

    const diasHTML = climas.map(d => `
        <div class="clima-card-dia">
            <span class="dia-label">${d.label.split(',')[0]}</span>
            <img src="https://openweathermap.org/img/wn/${d.icone}.png" />
            <span class="dia-temp">${d.temp}°</span>
            ${d.replicado ? '<span class="dia-est">~est.</span>' : ''}
        </div>
    `).join('');

    container.innerHTML = `
        <div class="clima-cidade">🌤 ${cidade}</div>
        <div class="clima-periodo">${primeiroDia} → ${ultimoDia}</div>
        <div class="clima-dias-wrapper">
            ${diasHTML}
        </div>
        <div class="clima-rodape">~est. = estimativa baseada no padrão atual</div>
    `;

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            const icones = container.querySelectorAll('.clima-card-dia img');
            icones.forEach((img, i) => {
                img.style.opacity = '0';
                img.style.transform = 'scale(0.8)';

                setTimeout(() => {
                    img.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                    img.style.opacity = '1';
                    img.style.transform = 'scale(1)';

                    setTimeout(() => {
                        img.style.animation = `pulseClima 2.5s ease-in-out ${i * 0.3}s infinite`;
                    }, 400);
                }, i * 150);
            });
        });
    });
}

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

/* WIDGET CLIMA */
function injetarTabelaClima() {
    if (document.querySelector('.tabela-destinos')) return;

    const div = document.createElement('div');
    div.className = 'tabela-destinos';
    div.innerHTML = `<div style="color:#444; font-size:0.75rem; text-align:center;">🌤 Clima aparecerá após informar o destino e as datas.</div>`;
    document.body.appendChild(div);
}

/**OBSERVAR CHAT — destino e datas*/
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

                    if (texto.includes('Qual é o destino da sua viagem')) {
                        aguardandoDestino = true;
                        return;
                    }

                    if (texto.includes('data de partida')) {
                        aguardandoDataIda = true;
                        return;
                    }
                    if (texto.includes('data de volta')) {
                        aguardandoDataVolta = true;
                        return;
                    }
                    if (texto.includes('LLMs podem cometer erros')) return;

                    if (aguardandoDestino && texto.length <= 40) {
                        destinoAtual = texto;
                        aguardandoDestino = false;
                        return;
                    }

                    if (aguardandoDataIda && /\d{2}\/\d{2}\/\d{4}/.test(texto)) {
                        dataIdaAtual = texto;
                        aguardandoDataIda = false;
                        return;
                    }
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

/*INICIALIZAÇÃO*/
const observerGeral = new MutationObserver(() => {
    const welcomeScreen = document.querySelector('#welcome-screen');
    const loginForm = document.querySelector('form input[name="password"]');

    if (welcomeScreen && !loginForm) {
        injetarBoasVindas();
        injetarTabelaClima();
        injetarDrawerSeta();
        observarDestino();
        injetarSpinner();
    }
});

observerGeral.observe(document.body, { childList: true, subtree: true });
setTimeout(() => {
    const loginForm = document.querySelector('form input[name="password"]');
    if (!loginForm) {
        injetarTabelaClima();
        injetarDrawerSeta();
    }
}, 1000);

// Retirando o logo da tela de login 
function removeChainlitLoginLogo() {
    const logos = document.querySelectorAll("img.logo");
    logos.forEach(logo => {
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
            <a href="/registro" target="_blank" style="
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


const observer_button = new MutationObserver(() => {
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
                window.open('/registro', '_blank');
            };
        }
    });
});

observer_button.observe(document.body, {
    childList: true,
    subtree: true
});

function injetarDrawerSeta() {
    if (document.querySelector('.drawer-seta')) return;

    const seta = document.createElement('button');
    seta.className = 'drawer-seta';
    seta.id = 'drawer-seta';
    seta.innerHTML = '🌤 ❯';

    seta.style.cssText = `
        display: none;
        position: fixed;
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        background: rgba(45, 45, 50, 0.95);
        border-radius: 8px 0 0 8px;
        padding: 12px 6px;
        cursor: pointer;
        z-index: 1000;
        border: 1px solid rgba(255,255,255,0.1);
        border-right: none;
        color: #d4d803;
        font-size: 1rem;
        writing-mode: vertical-lr;
        align-items: center;
        gap: 6px;
    `;

    document.body.appendChild(seta);

    function verificarTamanho() {
        if (window.innerWidth <= 768) {
            seta.style.display = 'flex';
        } else {
            seta.style.display = 'none';
        }
    }

    verificarTamanho();
    window.addEventListener('resize', verificarTamanho);

    seta.addEventListener('click', () => {
        const widget = document.querySelector('.tabela-destinos');
        const aberto = widget.classList.toggle('aberto');
        seta.innerHTML = aberto ? '🌤 ❮' : '🌤 ❯';
        seta.style.right = aberto ? '260px' : '0';
    });
}