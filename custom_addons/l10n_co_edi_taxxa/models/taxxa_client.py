# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
"""Cliente HTTP para la API de TAXXA (https://taxxa.co).

IMPORTANTE — disciplina de esta integración: cada campo/endpoint usado
acá está tomado directamente de la documentación técnica PÚBLICA de
TAXXA (https://taxxa.info/menu-manual-tecnico/), no se inventó nada.
Donde la documentación pública no alcanza, se deja marcado
explícitamente con "NO DOCUMENTADO / REQUIERE CONFIRMACIÓN CON TAXXA"
en vez de adivinar — un campo mal adivinado en un envío fiscal real es
peor que no tenerlo.

Confirmado en la documentación pública (fuente: taxxa.info):
  * Todas las llamadas son al MISMO endpoint base (una URL única por
    cuenta/dominio que asigna TAXXA — no hay una ruta por recurso como
    en un API REST tradicional). El "método" va DENTRO del JSON.
  * Convención de request: {"jApi": {"sMethod": "...", "jParams": {...}}}
    (y para llamadas autenticadas, "sToken" a nivel raíz del JSON).
  * Token: sMethod "classTaxxa.fjTokenGenerate", con sEmail/sPass en
    jParams. Respuesta: {"rerror": 0, "jret": {"raccount": ..., "stoken":
    ..., "texpires": "<fecha ISO>"}}.

CONFIRMADO EN VIVO (11/09/2026, contra el sandbox público demo1 —
NO se inventó, se probó con peticiones reales y se ajustó según los
errores reales que devolvió TAXXA):
  * fjDocumentAdd NO lleva "wEnviroment" como parámetro — el ambiente
    lo determina la cuenta/URL, no el JSON (a diferencia de lo que
    sugiere el manual del documento POS).
  * La estructura real confirmada es:
        jParams: {
            wVersionUBL: 2.1,
            jDocument: {
                <campos de encabezado: tissuedate, wdocumenttype, ...>,
                jbuyer: {...},       # todo en minúscula, ANIDADO
                jseller: {...},      # dentro de jDocument, no al lado
                jdocumentitems: {...},
                jtotalescop: {...},
            }
        }
    (el manual público sugiere que jbuyer/jseller/etc. van al mismo
    nivel que jDocument — en la práctica el servidor los rechaza ahí;
    solo los acepta anidados dentro de jDocument).
  * El vendedor (jseller) debe estar PRE-REGISTRADO en TAXXA por NIT
    antes de poder facturar — enviar el NIT real de Grupo Rico Pollo
    contra el sandbox público de demo devolvió: rerror 3344, "The
    seller document document ... was not found in the DB." Con la
    cuenta real que asigne TAXXA esto no debería pasar, pero confirma
    que el alta del NIT en su plataforma es un paso de onboarding
    obligatorio, no solo tener usuario/clave.
  * Los errores tienen DOS formas vistas: {"rerror": N, "serrormessage":
    "..."} para errores de parámetros/estructura, y {"rerror": N,
    "smessage": "..."} para errores de negocio (como el del NIT). El
    cliente de abajo revisa ambos campos.

CONFIRMADO CON CREDENCIALES REALES (12/09/2026 — Grupo Rico Pollo ya
tiene usuario/clave/URL reales de TAXXA para el ambiente de pruebas):
  * TAXXA compartió ejemplos JSON completos y reales (no solo tablas
    de campos) para factura, nota crédito y nota débito — están
    guardados literalmente en examples/*.json (ver examples/README.md
    para las inconsistencias de mayúsculas/minúsculas confirmadas
    entre ellos, que hay que respetar tal cual al mapear cada tipo de
    documento, no "corregir").
  * Con el NIT real de Grupo Rico Pollo (901909286) como vendedor:
    rerror 3344 — el NIT todavía no está dado de alta en la cuenta de
    TAXXA (paso de onboarding pendiente de ellos, no de este código).
  * Con el NIT de ejemplo de su propia documentación (901402281):
    rerror 9371, "Error actualizacion, Documento NO Generado" — error
    genérico, probable causa: los códigos de departamento/ciudad
    (wdepartmentcode/wtowncode) deben ser códigos EXACTOS del catálogo
    DIAN, no un número cualquiera — pendiente confirmar ese catálogo.

NO DOCUMENTADO / REQUIERE CONFIRMACIÓN CON TAXXA (no se pudo probar
más allá de este punto sin un NIT ya dado de alta en su plataforma):
  * La estructura exacta de la RESPUESTA cuando el documento SÍ se
    acepta — dónde viene el CUFE, el QR, el estado, o los enlaces al
    XML/PDF. submit_document() devuelve el JSON crudo tal cual llega,
    sin intentar interpretarlo, hasta ver una respuesta real de éxito.
  * El catálogo real de códigos de departamento/ciudad que exige TAXXA.
"""
import logging

import requests
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class TaxxaClient:
    def __init__(self, base_url):
        """:param base_url: URL única que TAXXA asigna por cuenta/dominio.
        No hay una URL genérica válida para producción — la de los
        manuales públicos (taxxaapi.com/api.djson?demo1) es solo de
        demostración.
        """
        if not base_url:
            raise UserError(_("Falta configurar la URL de la API de TAXXA (la asigna TAXXA por cuenta)."))
        self.base_url = base_url

    def _call(self, payload):
        """OJO (confirmado en vivo, no documentado): TAXXA responde con
        HTTP 400 —no 200— cuando "rerror" viene distinto de 0 (ej. clave
        incorrecta). Por eso NO se usa response.raise_for_status(): eso
        ocultaría el JSON real del error (serrormessage/smessage) detrás
        de un genérico "400 Bad Request". Se intenta leer el JSON
        siempre, sin importar el código HTTP, y es _raise_if_error()
        quien decide si hay que fallar."""
        try:
            response = requests.post(self.base_url, json=payload, timeout=DEFAULT_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise UserError(_("No se pudo conectar con TAXXA: %s", e))
        try:
            data = response.json()
        except ValueError:
            # Confirmado en vivo (12/09/2026): TAXXA tiene un firewall por
            # IP ("ParetoFW") — si el servidor que llama no está en su
            # lista blanca, responde 403 con una página HTML (no JSON)
            # pidiendo contactar a soporte con la IP. Se detecta ese caso
            # puntual para dar un mensaje accionable en vez de un genérico
            # "403 Forbidden".
            if response.status_code == 403 and 'Acceso Restringido' in response.text:
                raise UserError(_(
                    "TAXXA bloqueó la conexión por IP no autorizada (firewall ParetoFW). "
                    "Hay que pedirle a soporte de TAXXA que autorice la IP de este "
                    "servidor — el mensaje de ellos trae la IP exacta a reportar."))
            response.raise_for_status()
            raise UserError(_("TAXXA respondió algo que no es JSON válido:\n%s", response.text[:500]))
        return data

    def _raise_if_error(self, data):
        """TAXXA usa dos campos distintos según el tipo de error
        (confirmado probando en vivo, no está documentado así): errores
        de parámetros/estructura vienen en "serrormessage"; errores de
        negocio (ej. NIT no registrado) vienen en "smessage"."""
        if data.get("rerror"):
            message = data.get("serrormessage") or data.get("smessage") or str(data)
            raise UserError(_("TAXXA devolvió un error (%(code)s): %(message)s",
                               code=data.get("rerror"), message=message))

    def get_token(self, email, password):
        """Solicita un token nuevo. Confirmado en taxxa.info/solicitud-de-token/
        y probado en vivo contra el sandbox público.

        :returns: tupla (account, token) — el token trae también
            "texpires" (fecha de expiración) en la respuesta real,
            aunque no estaba documentado; se ignora por ahora, no hace
            falta para el flujo de renovación manual.
        """
        payload = {
            "jApi": {
                "sMethod": "classTaxxa.fjTokenGenerate",
                "jParams": {
                    "sEmail": email,
                    "sPass": password,
                },
            }
        }
        data = self._call(payload)
        self._raise_if_error(data)
        jret = data.get("jret") or {}
        account = jret.get("raccount")
        token = jret.get("stoken")
        if not token:
            raise UserError(_("TAXXA no devolvió un token. Respuesta completa:\n%s", data))
        return account, token

    def submit_document(self, token, document_payload):
        """Envía una factura o documento POS ya armado.

        :param document_payload: el contenido de "jDocument" —
            encabezado + jbuyer/jseller/jdocumentitems/jtotalescop
            TODOS anidados adentro (confirmado en vivo: el manual
            público sugiere que van al mismo nivel que jDocument, pero
            el servidor solo los acepta anidados adentro). NO incluir
            "wEnviroment": confirmado en vivo que fjDocumentAdd lo
            rechaza como parámetro inválido — el ambiente lo determina
            la cuenta/URL, no el JSON.

        La forma del RESPONSE en caso de ÉXITO no está documentada
        públicamente y no se pudo observar en vivo (el sandbox público
        no tiene registrado ningún NIT real para probar más allá de la
        validación de estructura) — se devuelve tal cual la entregue
        TAXXA, sin interpretar campos que todavía no se han confirmado
        (CUFE/QR/estado/XML/PDF).
        """
        payload = {
            "sToken": token,
            "jApi": {
                "sMethod": "classTaxxa.fjDocumentAdd",
                "jParams": {
                    "wVersionUBL": 2.1,
                    "jDocument": document_payload,
                },
            },
        }
        data = self._call(payload)
        _logger.info("Respuesta cruda de TAXXA (fjDocumentAdd), pendiente de mapear: %s", data)
        return data
