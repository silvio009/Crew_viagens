import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import markdown as md

def enviar_email(destinatario: str, assunto: str, corpo: str):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")

    try:
        corpo_html = md.markdown(corpo, extensions=["tables", "nl2br", "fenced_code"])

        html = f"""
        <html>
        <head>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Georgia', serif;
                    background-color: #e8e8e8;
                }}
                .wrapper {{
                    max-width: 680px;
                    margin: 40px auto;
                }}
                .header {{
                    background-color: #1b2631;
                    padding: 35px 40px;
                    text-align: center;
                }}
                .header h1 {{
                    color: #c9a84c;
                    font-size: 22px;
                    letter-spacing: 4px;
                    text-transform: uppercase;
                    font-weight: normal;
                }}
                .header p {{
                    color: #a0a0a0;
                    font-size: 11px;
                    letter-spacing: 3px;
                    text-transform: uppercase;
                    margin-top: 6px;
                }}
                .divider-gold {{
                    background-color: #1b2631;
                    padding: 6px 40px;
                    text-align: center;
                }}
                .divider-gold span {{
                    display: inline-block;
                    width: 80px;
                    height: 1px;
                    background-color: #c9a84c;
                    vertical-align: middle;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 45px 50px;
                    color: #2c2c2c;
                    font-size: 14px;
                    line-height: 1.9;
                }}
                .content p {{
                    margin-bottom: 16px;
                    color: #3a3a3a;
                }}
                .content h2 {{
                    font-family: 'Arial', sans-serif;
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 3px;
                    text-transform: uppercase;
                    color: #1b2631;
                    margin: 35px 0 15px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #c9a84c;
                }}
                .content h3 {{
                    font-family: 'Arial', sans-serif;
                    font-size: 12px;
                    font-weight: bold;
                    color: #555555;
                    margin: 20px 0 8px;
                    letter-spacing: 1px;
                }}
                .content ul {{
                    padding-left: 18px;
                    margin-bottom: 16px;
                }}
                .content ul li {{
                    margin-bottom: 8px;
                    color: #3a3a3a;
                }}
                .content ol {{
                    padding-left: 18px;
                    margin-bottom: 16px;
                }}
                .content ol li {{
                    margin-bottom: 8px;
                    color: #3a3a3a;
                }}
                .content strong {{
                    color: #1b2631;
                    font-weight: bold;
                }}
                .content hr {{
                    border: none;
                    border-top: 1px solid #e8e8e8;
                    margin: 25px 0;
                }}
                .content table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-family: 'Arial', sans-serif;
                    font-size: 13px;
                }}
                .content table th {{
                    background-color: #1b2631;
                    color: #c9a84c;
                    padding: 12px 15px;
                    text-align: left;
                    letter-spacing: 1px;
                    font-size: 11px;
                    text-transform: uppercase;
                }}
                .content table td {{
                    padding: 11px 15px;
                    border-bottom: 1px solid #efefef;
                    color: #3a3a3a;
                }}
                .content table tr:last-child td {{
                    font-weight: bold;
                    background-color: #f7f3ea;
                    color: #1b2631;
                    border-bottom: none;
                }}
                .sign-off {{
                    background-color: #f9f9f9;
                    padding: 25px 50px;
                    border-top: 1px solid #e8e8e8;
                    font-family: 'Arial', sans-serif;
                    font-size: 13px;
                    color: #555555;
                    line-height: 2;
                }}
                .sign-off strong {{
                    color: #1b2631;
                    font-size: 14px;
                    letter-spacing: 1px;
                }}
                .footer {{
                    background-color: #1b2631;
                    padding: 20px 40px;
                    text-align: center;
                }}
                .footer p {{
                    color: #a0a0a0;
                    font-size: 11px;
                    letter-spacing: 1px;
                    line-height: 2;
                }}
                .footer a {{
                    color: #c9a84c;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">

                <div class="header">
                    <h1>TravelCrew Agency</h1>
                    <p>Excelência em experiências de viagem</p>
                </div>

                <div class="divider-gold">
                    <span></span>
                </div>

                <div class="content">
                    {corpo_html}
                </div>

                <div class="sign-off">
                    <strong>Equipe TravelCrew Agency</strong><br>
                    📧 contato@travelcrew.com.br<br>
                    📞 (11) 9999-9999<br>
                    🌐 <a href="http://www.travelcrew.com.br">www.travelcrew.com.br</a>
                </div>

                <div class="footer">
                    <p>
                        Este email foi enviado exclusivamente para você.<br>
                        © 2025 TravelCrew Agency. Todos os direitos reservados.
                    </p>
                </div>

            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = destinatario

        parte_texto = MIMEText(corpo, "plain", "utf-8")
        parte_html = MIMEText(html, "html", "utf-8")

        msg.attach(parte_texto)
        msg.attach(parte_html)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatario, msg.as_string())
        return True

    except Exception as e:
        return False