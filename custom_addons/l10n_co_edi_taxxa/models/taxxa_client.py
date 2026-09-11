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
    la primera vez rerror 9371 ("Documento NO Generado, intente de
    nuevo") — genérico. Reintentando con la fecha correcta (ver
    siguiente punto) sí avanzó hasta la DIAN de verdad.
  * TAXXA tiene firewall por IP ("ParetoFW") — confirmado y ya resuelto
    para el servidor de producción (ver _call(), detección del 403 con
    la página "Acceso Restringido").
  * IMPORTANTE: la fecha de emisión (tissuedate) NO puede ser futura
    respecto al reloj real de TAXXA/DIAN — un envío con la fecha de
    "mañana" fue rechazado con rerror 84133 y el propio mensaje trae
    los timestamps Unix de "ahora" y del límite permitido, útiles para
    depurar si esto vuelve a pasar.

CONFIRMADO — LLEGÓ HASTA LA DIAN DE VERDAD (12/09/2026): con NIT
901402281, fecha correcta y la estructura de examples/invoice_con_propina.json,
la respuesta ya NO fue un error de TAXXA sino un rechazo real y firmado
de la DIAN (visto: request llegó completo, firmado XAdES, con
ProviderID de TAXXA ante la DIAN). Esto confirma que TODA la tubería
(Odoo → TAXXA → DIAN) funciona técnicamente. El documento fue
RECHAZADO por reglas de negocio reales de la DIAN (numeración no
autorizada para ese NIT/prefijo, nombre del vendedor no coincide con
el RUT, departamento/municipio inconsistentes) — no por un problema de
integración. Ejemplo completo guardado en
examples/dian_response_rejected_example.xml.

Estructura de la respuesta ya confirmada (antes marcada como "no
documentada"):
  * Éxito o rechazo, ambos devuelven HTTP 400/200 con:
    {"rerror": N, "smessage": {"string": {"0": "...", ...}} (lista de
    reglas violadas si rechaza), "jret": {"sreturnedxml": "<XML de la
    DIAN, en base64>"}}.
  * El XML decodificado es un ApplicationResponse UBL firmado. Dentro:
    - <cbc:ResponseCode>04</cbc:ResponseCode> + <cbc:Description> =
      resultado a nivel de documento ("04" = rechazado por la DIAN).
    - Una lista de <cbc:ResponseCode>/<cbc:Description> por cada regla
      violada (ej. "CDG01" = departamento no coincide con municipio).
    - El CUFE SÍ se genera aunque el documento sea rechazado (es un
      hash determinístico del contenido, no algo que la DIAN "asigna"
      solo si acepta) — está en
      <cbc:UUID schemeName="CUFE-SHA384">...</cbc:UUID>.
  * Pendiente ver un ApplicationResponse de ACEPTACIÓN real (no se
    logró: haría falta una numeración/resolución realmente autorizada
    para el NIT de prueba, y el nombre legal exacto del RUT) — pero la
    UBICACIÓN del CUFE ya no es una incógnita, y lo demás (QR/PDF) se
    puede resolver una vez el documento sí sea aceptado, con las APIs
    de descarga ya confirmadas (api-bajar-xml, api-consultar-factura).

NO DOCUMENTADO / REQUIERE CONFIRMACIÓN CON TAXXA:
  * El catálogo real de códigos de departamento/ciudad — sin él no se
    puede armar un envío que la DIAN acepte, solo rechazos "correctos".
  * Confirmar si el rechazo de prueba fue por datos genuinos mal
    armados de este lado, o si el ambiente de pruebas de TAXXA siempre
    devuelve el mismo rechazo "canned" sin importar el contenido
    enviado (el sdocumentprefix que la DIAN reportó en la respuesta,
    "SETP", no coincide con el que se envió, "PRU" — sugiere que sí
    podría ser una respuesta fija de demostración, no un reflejo
    dinámico de cada envío).
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
