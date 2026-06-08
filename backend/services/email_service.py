"""
Servicio de envío de correos electrónicos vía SMTP (Gmail).
Usa smtplib y email.mime de la stdlib — sin dependencias externas.

Email sending service via SMTP (Gmail).
Uses smtplib and email.mime from stdlib — no external dependencies.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import get_settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Envía un correo electrónico HTML vía SMTP.
    Retorna True si se envió correctamente, False si falló.

    Sends an HTML email via SMTP.
    Returns True if sent successfully, False if it failed.
    """
    settings = get_settings()

    if not settings.smtp_user or not settings.smtp_password:
        logger.error("SMTP no configurado: SMTP_USER y SMTP_PASSWORD son requeridos en .env")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to, msg.as_string())

        logger.info(f"Correo enviado exitosamente a {to}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Error de autenticación SMTP: verifica SMTP_USER y SMTP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP al enviar correo a {to}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al enviar correo a {to}: {e}")
        return False


def send_reset_code(to: str, code: str, expire_minutes: int) -> bool:
    """
    Envía un correo con el código de recuperación de contraseña.

    Sends an email with the password reset code.
    """
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;
                padding: 30px; background-color: #f9fafb; border-radius: 12px;">
        <div style="background-color: #4f46e5; padding: 20px; border-radius: 8px 8px 0 0;
                    text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 22px;">
                🔐 Recuperación de Contraseña
            </h1>
        </div>
        <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px;
                    border: 1px solid #e5e7eb; border-top: none;">
            <p style="color: #374151; font-size: 15px; margin-top: 0;">
                Has solicitado restablecer tu contraseña.
                Usa el siguiente código para continuar:
            </p>
            <div style="background-color: #eef2ff; border: 2px dashed #4f46e5;
                        border-radius: 8px; padding: 20px; text-align: center;
                        margin: 20px 0;">
                <span style="font-size: 36px; font-weight: bold; color: #4f46e5;
                             letter-spacing: 8px;">
                    {code}
                </span>
            </div>
            <p style="color: #6b7280; font-size: 13px; margin-bottom: 0;">
                ⏱️ Este código expira en <strong>{expire_minutes} minutos</strong>.<br>
                Si no solicitaste este cambio, ignora este correo.
            </p>
        </div>
        <p style="text-align: center; color: #9ca3af; font-size: 11px; margin-top: 16px;">
            Sistema de Extracción de Cédulas
        </p>
    </div>
    """
    return send_email(to, "Código de recuperación de contraseña", html_body)
