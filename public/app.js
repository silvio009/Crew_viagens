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

window.addEventListener('load', () => {
    setTimeout(injetarSpinner, 500);
});

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

window.addEventListener('load', () => {
    setTimeout(injetarBoasVindas, 600);
});