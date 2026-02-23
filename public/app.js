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

    .loader-shimmer {
        background: linear-gradient(
            90deg,
            #888888 25%,
            #ffffff 50%,
            #888888 75%
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 1.5s linear infinite;
        display: inline-block;
    }

    .spinner-viagem {
        display: inline-block;
        margin-left: 6px;
        vertical-align: middle;
        width: 14px;
        height: 14px;
        border: 2px solid #ffffff44;
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin-viagem 0.7s linear infinite;
        flex-shrink: 0;
    }

    .loader-wrapper {
        display: inline-flex !important;
        align-items: center !important;
        white-space: nowrap !important;
    }

    div[role="article"]:has(.loader-wrapper) {
        display: flex !important;
        justify-content: flex-start !important;
        padding: 0 !important;
        margin: 0 !important;
        text-indent: 0 !important;
        line-height: normal !important;
    }
    .tabela-destinos {
        position: fixed;
        right: 20px;
        top:75px;   
        z-index: 9999;
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
        gap: 6px;
        background: transparent; 
        box-shadow: none;        
        padding: 0;              
    }

    .clima-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .clima-header img {
        width: 38px;
    }

    .clima-temp {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffffff;
        line-height: 1;
    }

    .clima-desc {
        font-size: 0.75rem;
        color: #aaaaaa;
        text-transform: capitalize;
    }

    .clima-cidade {
        font-size: 0.7rem;
        color: #888888;
    }

    .clima-input {
        width: 140px;
        background: transparent;
        border: none;
        border-bottom: 1px solid #444;
        padding: 4px 0;
        color: #ccc;
        font-size: 0.75rem;
        outline: none;
    }

    .clima-input::placeholder {
        color: #666;
    }

    .clima-input:focus {
        border-bottom: 1px solid #888;
    }
`;
document.head.appendChild(style);

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

window.addEventListener('load', () => {
    setTimeout(injetarSpinner, 600);
});

async function buscarClima(cidade) {
    try {
        console.log('🌎 [CLIMA] Iniciando requisição para:', cidade);

        let apiKey = window._owKey;
        if (!apiKey) {
            await new Promise(r => setTimeout(r, 1000));
            apiKey = window._owKey;
        }

        if (!apiKey) {
            console.log('❌ API key não encontrada');
            return null;
        }

        const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(cidade)}&appid=${apiKey}&units=metric&lang=pt_br`;

        console.log('📡 URL:', url);

        const res = await fetch(url);
        const data = await res.json();

        if (data.cod !== 200) {
            console.log('⚠️ Cidade não encontrada');
            return null;
        }

        return {
            cidade: data.name,
            temp: Math.round(data.main.temp),
            descricao: data.weather[0].description,
            icone: data.weather[0].icon
        };

    } catch (e) {
        console.error('💥 Erro na requisição:', e);
        return null;
    }
}

async function atualizarClimaTabela(cidade) {

    // 🔥 Cria o widget SOMENTE quando tiver destino
    if (!document.querySelector('.tabela-destinos')) {
        injetarTabelaClima();
    }

    const clima = await buscarClima(cidade);
    if (!clima) return;

    console.log('🌡 Atualizando widget com clima de:', cidade);

    document.querySelector('.clima-temp').innerText = `${clima.temp}°C`;
    document.querySelector('.clima-desc').innerText = clima.descricao;
    document.querySelector('.clima-cidade').innerText = clima.cidade;

    document.getElementById('clima-icone').src =
        `https://openweathermap.org/img/wn/${clima.icone}@2x.png`;
}
/**
 * 3. BOAS-VINDAS
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
            <p style="font-size:1.1rem; color:#aaaaaa; margin:0 0 4px;">
                Olá, viajante!
            </p>
            <p style="font-size:0.85rem; color:#666; margin:0;">
                Digite sua cidade de origem para começar.
            </p>
        `;
        welcomeScreen.insertBefore(div, input);
    }
}

/**
 * 4. WIDGET CLIMA
 */
function injetarTabelaClima() {
    if (document.querySelector('.tabela-destinos')) return;

    const div = document.createElement('div');
    div.className = 'tabela-destinos';
    div.innerHTML = `
        <div class="clima-header">
            <img src="" id="clima-icone" />
            <div>
                <div class="clima-temp">--°C</div>
                <div class="clima-desc">Aguardando...</div>
                <div class="clima-cidade">Destino</div>
            </div>
        </div>

    `;

    document.body.appendChild(div);
}

/**
 * 5. OBSERVAR DESTINO (BLINDADO)
 */
let aguardandoDestino = false;
let ultimoDestino = '';
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
                    : node.querySelectorAll?.('[role="article"]');

                if (!artigos) return;

                artigos.forEach((artigo) => {

                    const texto = artigo.innerText.trim();
                    if (!texto) return;

                    if (texto.includes('Qual é o destino da sua viagem')) {
                        console.log('🤖 Bot perguntou destino');
                        aguardandoDestino = true;
                        return;
                    }

                    if (
                        texto.includes('LLMs podem cometer erros') ||
                        texto.includes('Verifique informações')
                    ) {
                        return;
                    }

                    if (!aguardandoDestino) return;
                    if (texto.length > 40) return;
                    if (texto === ultimoDestino) return;

                    console.log('🎯 Destino válido detectado:', texto);

                    ultimoDestino = texto;
                    aguardandoDestino = false;

                    atualizarClimaTabela(texto);

                });

            });

        });

    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log("👀 Observer iniciado (modo blindado)");
}

/**
 * 6. INICIALIZAÇÃO
 */
const observerGeral = new MutationObserver(() => {
    const welcomeScreen = document.querySelector('#welcome-screen');

    if (welcomeScreen) {
        injetarBoasVindas();
        observarDestino();
        injetarSpinner();
    }
});

observerGeral.observe(document.body, { childList: true, subtree: true });