# ERP Colombia — Checklist de preparación para producción

Estado al 2026-08-26 (post-reconstrucción). Distingue lo ya resuelto de
lo que requiere una decisión o trámite que solo tú puedes hacer.

## 1. Seguridad — hecho aquí
- [x] `admin_passwd`/`db_password` cambiados de los valores por defecto.
- [x] `odoo.conf`/`odoo_demo.conf` (con contraseñas reales) fuera de
      git — solo se versiona `odoo.conf.example`.
- [x] Servidores escuchando solo en `127.0.0.1`.

## 2. Seguridad — pendiente antes de exponer a internet
- [ ] `list_db = False` en `odoo.conf` (ya activo en `odoo_demo.conf`).
- [ ] Proxy HTTPS real (Nginx/Caddy) — nunca exponer 8069/8070 directo.
- [ ] `proxy_mode = True` cuando se agregue el proxy.
- [ ] Firewall: solo 80/443 públicos.

## 3. Infraestructura — decisión de negocio
- [ ] Elegir dónde correrá producción (este Mac es solo desarrollo).
- [ ] Dominio propio y DNS.
- [ ] Dimensionar `workers`/`max_cron_threads` según el servidor real.
- [ ] Política de correo saliente (SMTP).

## 4. Respaldos — PENDIENTE, prioridad alta tras el incidente del 2026-08-26
- [x] `scripts/backup.sh` (pg_dump + filestore) — probado antes del
      incidente; recreado en la reconstrucción.
- [ ] **Repositorio remoto real** (GitHub privado u otro) — la pérdida
      total de archivos del 2026-08-26 solo fue recuperable porque el
      código seguía en el contexto de esta sesión de Claude. Un
      segundo incidente sin eso sería irrecuperable. Esta es ahora la
      tarea de mayor prioridad de todo el checklist.
- [ ] Automatizar `scripts/backup.sh` con cron/launchd.
- [ ] Copiar respaldos a almacenamiento externo/off-site (no solo este Mac).
- [ ] Habilitar Time Machine o equivalente en esta máquina (no estaba
      configurado — causa directa de no poder recuperar los archivos
      sin reconstruirlos a mano).

## 5. Facturación electrónica DIAN — trámite real, no código
- [ ] Inscripción como facturador electrónico "software propio" ante la DIAN.
- [ ] Software ID + PIN de habilitación reales.
- [ ] Certificado digital de firma válido para producción.
- [ ] Resolución de facturación con prefijo y rango autorizados.
- [ ] Pasar el set de pruebas de la DIAN.

## 6. Contabilidad
- [ ] Plantilla de cierre de año fiscal del PUC colombiano — decisión
      contable, el motor ya está instalado y probado.
- [ ] Revisar con un contador la tarifa de autorretención antes de
      activarla en producción.

## 7. Código y versionado
- [x] Todo el trabajo propio versionado en git localmente (perdido y
      reconstruido una vez el 2026-08-26 — ver `ARCHITECTURE.md`).
- [ ] **Repositorio remoto** (repetido de la sección 4 a propósito: es
      la brecha más importante detectada).
- [ ] Definir quién puede hacer `git push` y un proceso de revisión.

## 8. Pruebas antes de ir en vivo
- [x] Flujo integral completo probado (contactos, compras, ventas,
      factura electrónica demo, kardex, balance, cierre contable).
- [x] Motor de datos DEMO probado en SMALL y STANDARD (5/5 validaciones).
- [ ] Repetir la facturación electrónica contra el ambiente de
      habilitación real de la DIAN (no demo) con credenciales reales.
- [ ] Validar con el contador de la empresa un mes real de datos.
