/**
 * 1. CONFIGURAÇÃO E ESTILOS
 */
const configScript = document.createElement('script');
configScript.src = '/public/config.js?t=' + Date.now();
document.head.appendChild(configScript);

const style = document.createElement('style');
style.textContent = `
    .tabela-destinos {
        position: fixed;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 9999;
        background: #1a1a1a;
        border-radius: 8px;
        padding: 10px 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.4);
        width: 250px; /* menor */
        font-family: sans-serif;
        font-size: 0.8rem; /* texto menor */
    }

    .tabela-destinos input {
        width: 100%;
        background: #111;
        border: 1px solid #2a2a2a;
        border-radius: 5px;
        padding: 6px;
        color: #aaa;
        margin-bottom: 6px;
        font-size: 0.75rem;
    }

    .tabela-destinos button {
        width: 100%;
        background: #2a2a2a;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 6px;
        color: #aaa;
        cursor: pointer;
        margin-bottom: 8px;
        font-size: 0.75rem;
    }

    .tabela-destinos img {
        width: 28px; /* ícone menor */
    }
`;
document.head.appendChild(style);

/**
 * 2. API
 */
async function buscarClima(cidade) {
    try {
        console.log('🌎 [CLIMA] Iniciando requisição para:', cidade);

        let apiKey = window._owKey;
        if (!apiKey) {
            console.log('🔑 [CLIMA] Aguardando API key...');
            await new Promise(r => setTimeout(r, 1000));
            apiKey = window._owKey;
        }

        if (!apiKey) {
            console.log('❌ [CLIMA] API key não encontrada');
            return null;
        }

        const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(cidade)}&appid=${apiKey}&units=metric&lang=pt_br`;

        console.log('📡 [CLIMA] URL:', url);

        const res = await fetch(url);
        const data = await res.json();

        console.log('📥 [CLIMA] Resposta da API:', data);

        if (data.cod !== 200) {
            console.log('⚠️ [CLIMA] Cidade não encontrada');
            return null;
        }

        console.log('✅ [CLIMA] Clima recebido com sucesso');

        return {
            cidade: data.name,
            temp: Math.round(data.main.temp),
            descricao: data.weather[0].description,
            icone: data.weather[0].icon
        };

    } catch (e) {
        console.error('💥 [CLIMA] Erro na requisição:', e);
        return null;
    }
}

async function atualizarClimaTabela(cidade) {
    const resultado = document.getElementById('clima-resultado');
    if (!resultado) return;

    resultado.innerHTML = '<span style="color:#555">Buscando...</span>';

    const clima = await buscarClima(cidade);

    if (!clima) {
        resultado.innerHTML = '<span style="color:#ff6b6b">Não encontrado.</span>';
        return;
    }

    document.getElementById('clima-cidade').value = cidade;

    resultado.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px;">
            <img src="https://openweathermap.org/img/wn/${clima.icone}.png" width="40"/>
            <div>
                <div style="color:#fff; font-weight:600;">${clima.temp}°C</div>
                <div style="color:#888; font-size:0.75rem;">${clima.descricao}</div>
                <div style="color:#555; font-size:0.65rem;">${clima.cidade}</div>
            </div>
        </div>
    `;
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
 * 4. TABELA CLIMA (SÓ DESTINO)
 */
function injetarTabelaClima() {
    if (document.querySelector('.tabela-destinos')) return;

    const div = document.createElement('div');
    div.className = 'tabela-destinos';
    div.innerHTML = `
        <p style="font-size:0.7rem; color:#555; margin-bottom:10px;">
            🌤 Clima no destino
        </p>

        <input id="clima-cidade" type="text" placeholder="Digite o destino"
            style="width:100%; background:#111; border:1px solid #2a2a2a;
            border-radius:6px; padding:8px; color:#aaa; margin-bottom:8px;"/>

        <button id="clima-btn"
            style="width:100%; background:#2a2a2a; border:1px solid #333;
            border-radius:6px; padding:8px; color:#aaa; cursor:pointer; margin-bottom:10px;">
            🔍 Verificar clima
        </button>

        <div id="clima-resultado"
            style="color:#666; text-align:center; min-height:40px;">
            Digite um destino.
        </div>
    `;

    document.body.appendChild(div);

    document.getElementById('clima-btn').addEventListener('click', () => {
        const cidade = document.getElementById('clima-cidade').value.trim();
        if (cidade) atualizarClimaTabela(cidade);
    });
}

/**
 * 5. OBSERVAR DESTINO
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

                    // 🔎 Detecta pergunta do bot
                    if (texto.includes('Qual é o destino da sua viagem')) {
                        console.log('🤖 Bot perguntou destino');
                        aguardandoDestino = true;
                        return;
                    }

                    // 🛑 Ignorar textos do sistema
                    if (
                        texto.includes('LLMs podem cometer erros') ||
                        texto.includes('Verifique informações')
                    ) {
                        return;
                    }

                    // 🛑 Ignorar se não estamos aguardando
                    if (!aguardandoDestino) return;

                    // 🛑 Ignorar textos muito longos (cidade não é texto grande)
                    if (texto.length > 40) return;

                    // 🛑 Evitar repetir o mesmo destino
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
        injetarTabelaClima();
        observarDestino();
    }
});

observerGeral.observe(document.body, { childList: true, subtree: true });

