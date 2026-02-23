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
`;
document.head.appendChild(style);

function injetarSpinner() {
    const observer = new MutationObserver(() => {
        const mensagens = document.querySelectorAll('.prose div[role="article"]');
        mensagens.forEach((el) => {
            if (
                el.textContent.includes('Pesquisando e gerando seu roteiro') &&
                !el.querySelector('.loader-shimmer')
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

function injetarBoasVindas() {
    if (document.querySelector('.boas-vindas')) return;

    const welcomeScreen = document.querySelector('#welcome-screen');
    if (!welcomeScreen) return;

    const input = welcomeScreen.querySelector('#message-composer');
    if (!input) return;

    const div = document.createElement('div');
    div.className = 'boas-vindas';
    div.innerHTML = `
        <p style="font-size: 1.1rem; color: #aaaaaa; margin: 0 0 4px 0;">
            Olá, viajante!
        </p>
        <p style="font-size: 0.85rem; color: #666666; margin: 0;">
            Digite sua cidade de origem para começar.
        </p>
    `;
    div.style.cssText = `text-align: center; padding: 0 16px 12px 16px;`;

    welcomeScreen.insertBefore(div, input);
}

async function buscarClima(cidade) {
    try {
        // Aguarda a chave carregar
        let apiKey = window._owKey;
        if (!apiKey) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            apiKey = window._owKey;
        }

        console.log('API Key:', apiKey); // debug
        console.log('Cidade:', cidade);  // debug

        const res = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(cidade)}&appid=${apiKey}&units=metric&lang=pt_br`
        );
        const data = await res.json();
        console.log('Resposta:', data); // debug

        if (data.cod !== 200) return null;
        return {
            cidade: data.name,
            temp: Math.round(data.main.temp),
            descricao: data.weather[0].description,
            icone: data.weather[0].icon
        };
    } catch (e) {
        console.error('Erro:', e);
        return null;
    }
}

function injetarTabelaClima() {
    if (document.querySelector('.tabela-destinos')) return;

    const div = document.createElement('div');
    div.className = 'tabela-destinos';
    div.style.cssText = `
        position: fixed;
        right: 24px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 9999;
        background: #1a1a1a;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
        min-width: 210px;
        font-family: sans-serif;
    `;

    div.innerHTML = `
        <p style="font-size: 0.65rem; color: #555; margin: 0 0 10px 0; letter-spacing: 1.5px; text-transform: uppercase;">🌤 Clima no destino</p>
        
        <input id="clima-cidade" type="text" placeholder="Destino" style="
            width: 100%; box-sizing: border-box;
            background: #111; border: 1px solid #2a2a2a;
            border-radius: 6px; padding: 6px 10px;
            color: #aaa; font-size: 0.78rem; outline: none;
            margin-bottom: 6px;
        "/>

        <div style="display: flex; gap: 6px; margin-bottom: 6px;">
            <input id="clima-ida" type="date" style="
                flex: 1; background: #111; border: 1px solid #2a2a2a;
                border-radius: 6px; padding: 6px 8px;
                color: #aaa; font-size: 0.72rem; outline: none;
            "/>
            <input id="clima-volta" type="date" style="
                flex: 1; background: #111; border: 1px solid #2a2a2a;
                border-radius: 6px; padding: 6px 8px;
                color: #aaa; font-size: 0.72rem; outline: none;
            "/>
        </div>

        <button id="clima-btn" style="
            width: 100%; background: #2a2a2a; border: 1px solid #333;
            border-radius: 6px; padding: 7px; color: #aaa;
            font-size: 0.75rem; cursor: pointer; margin-bottom: 10px;
        ">🔍 Verificar clima</button>

        <div id="clima-resultado" style="
            color: #666; font-size: 0.78rem;
            text-align: center; min-height: 36px;
        ">
            Digite um destino e as datas.
        </div>
    `;

    document.body.appendChild(div);

    document.getElementById('clima-btn').addEventListener('click', async () => {
        const cidade = document.getElementById('clima-cidade').value.trim();
        const resultado = document.getElementById('clima-resultado');

        if (!cidade) {
            resultado.innerHTML = '<span style="color:#ff6b6b">Digite um destino.</span>';
            return;
        }

        resultado.innerHTML = '<span style="color:#555">Buscando...</span>';

        const clima = await buscarClima(cidade);
        if (!clima) {
            resultado.innerHTML = '<span style="color:#ff6b6b">Destino não encontrado.</span>';
            return;
        }

        resultado.innerHTML = `
            <div style="display:flex; align-items:center; justify-content:center; gap:8px;">
                <img src="https://openweathermap.org/img/wn/${clima.icone}.png" style="width:36px;height:36px;"/>
                <div style="text-align:left;">
                    <div style="color:#fff; font-size:1rem; font-weight:600;">${clima.temp}°C</div>
                    <div style="color:#888; font-size:0.7rem;">${clima.descricao}</div>
                    <div style="color:#555; font-size:0.65rem;">${clima.cidade}</div>
                </div>
            </div>
        `;
    });
}

// Usa MutationObserver para aguardar o welcome-screen existir
const observerTabela = new MutationObserver(() => {
    const welcomeScreen = document.querySelector('#welcome-screen');
    if (welcomeScreen && !document.querySelector('.tabela-destinos')) {
        injetarTabelaClima();
    }
});

observerTabela.observe(document.body, { childList: true, subtree: true });

window.addEventListener('load', () => {
    setTimeout(injetarSpinner, 500);
    setTimeout(() => {
        injetarBoasVindas();
        injetarTabelaDestinos();
    }, 600);
});