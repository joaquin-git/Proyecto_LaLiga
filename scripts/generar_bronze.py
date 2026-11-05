#!/usr/bin/env python3
"""
Genera las 6 tablas de la capa BRONZE (CSV) del proyecto "Moneyball LaLiga".

Uso:  python3 scripts/generar_bronze.py
Salida:
  data/bronze/*.csv                          -> ficheros que se cargan en Snowflake
  data/validacion/etiquetas_scouting.csv     -> "verdad" oculta para medir AI_CLASSIFY
  snowflake/02_bronze_laliga.sql             -> DDL + COPY INTO + permisos (generado a partir de las columnas)

Es determinista (semilla fija): siempre produce los mismos datos.
Los datos de rendimiento, salarios, lesiones, informes, agentes y ojeadores son SIMULADOS.
"""
import csv
import math
import random
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

import datos_maestros as M

SEMILLA = 2025
rnd = random.Random(SEMILLA)

RAIZ = Path(__file__).resolve().parents[1]
DIR_BRONZE = RAIZ / "data" / "bronze"
DIR_VALID = RAIZ / "data" / "validacion"
DIR_SQL = RAIZ / "snowflake"

FECHA_EXTRACCION = "2026-07-02 06:00:00"
FIN_DATOS = date(2026, 6, 30)

TEMPORADAS = [
    # nombre, primer viernes, clubes, (inicio ventana lesiones, fin)
    ("2024/25", date(2024, 8, 16), M.CLUBES_2425, date(2024, 7, 15), date(2025, 6, 1)),
    ("2025/26", date(2025, 8, 15), M.CLUBES_2526, date(2025, 7, 15), date(2026, 6, 1)),
]


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def poisson(lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= L:
            return k
        k += 1


def elegir_ponderado(items, pesos):
    total = sum(pesos)
    r = rnd.uniform(0, total)
    acc = 0
    for it, w in zip(items, pesos):
        acc += w
        if r <= acc:
            return it
    return items[-1]


def d(s):
    return date.fromisoformat(s)


def edad(fnac, en):
    return en.year - fnac.year - ((en.month, en.day) < (fnac.month, fnac.day))


def club_txt(c):
    """Nombre oficial de un club de LaLiga (código) o del club externo 'Club/Liga/País'."""
    if c in M.CLUBES:
        return M.CLUBES[c][0]
    return c.split("/")[0]


def club_liga_pais(c):
    if c in M.CLUBES:
        return M.CLUBES[c][0], "LaLiga EA Sports", "España"
    partes = c.split("/")
    if len(partes) == 3:
        return partes[0], partes[1], partes[2]
    return c, "", ""


def alias(club, fuente):
    of, corto, *_r, al = M.CLUBES[club]
    if fuente == "oficial":
        return of
    if fuente == "corto":
        return corto
    return rnd.choice(al + [of])


# ----------------------------------------------------------------------------
# 1. Jugadores
# ----------------------------------------------------------------------------
class Jugador:
    __slots__ = ("id", "nombre", "pos", "nac", "fnac", "estrella", "q", "licencia",
                 "id_prov", "agencia", "agente", "sesgo_salario", "remate")

    def __repr__(self):
        return f"<{self.nombre}>"


JUGADORES = []          # lista
POR_NOMBRE = {}         # nombre -> [Jugador] (hay homónimos: "Juan Cruz")


def parsear(bloque):
    out = []
    for linea in bloque.strip().splitlines():
        partes = linea.split("|")
        nombre, pos, nac, anio = partes[0], partes[1], partes[2], int(partes[3])
        flags = partes[4] if len(partes) > 4 else ""
        estrella = "*" in flags
        prop = None
        if "L=" in flags:
            prop = flags.split("L=")[1]
        out.append((nombre, pos, nac, anio, estrella, prop))
    return out


def crear_jugador(nombre, pos, nac, anio, estrella, club_inicial):
    j = Jugador()
    j.id = len(JUGADORES) + 1
    j.nombre, j.pos, j.nac, j.estrella = nombre, pos, nac, estrella
    j.fnac = date(anio, rnd.randint(1, 12), rnd.randint(1, 28))
    fuerza = M.CLUBES[club_inicial][4] if club_inicial in M.CLUBES else 0.3
    j.q = fuerza + rnd.gauss(0, 0.45) + (0.85 if estrella else 0)
    j.licencia = f"LIC-{100000 + j.id * 7}"
    j.id_prov = f"OPT-{50000 + rnd.randint(0, 49999)}"
    ag = rnd.choices(M.AGENCIAS, weights=[9, 8, 8, 4, 5, 5, 4, 6, 3, 5, 4, 2])[0]
    j.agencia, j.agente = ag, rnd.choice(ag[2])
    j.sesgo_salario = rnd.gauss(0, 0.38)   # lo que hace que haya "gangas" y "sobrepagados"
    j.remate = rnd.gauss(0, 0.2) + (0.45 if (estrella and pos == "DEL") else 0)
    JUGADORES.append(j)
    POR_NOMBRE.setdefault(nombre, []).append(j)
    return j


def buscar(nombre, club=None):
    lista = POR_NOMBRE[nombre]
    if len(lista) == 1 or club is None:
        return lista[0]
    for j in lista:
        if TRAMOS_ABIERTOS.get(j.id, {}).get("club") == club:
            return j
    return lista[0]


# ----------------------------------------------------------------------------
# 2. Tramos (jugador en un club entre dos fechas) a partir de plantillas + movimientos
# ----------------------------------------------------------------------------
TRAMOS = []             # dicts: jugador, club, desde, hasta, tipo, propietario
TRAMOS_ABIERTOS = {}    # jugador.id -> tramo abierto

MOVS = []
for linea in M.MOVIMIENTOS.strip().splitlines():
    f, nom, ori, des, tipo, imp = linea.split("|")
    MOVS.append(dict(fecha=d(f), jugador=nom, origen=ori, destino=des, tipo=tipo, importe=int(imp)))
MOVS.sort(key=lambda m: m["fecha"])

LLEGADAS_VERANO_2024 = {m["jugador"]: m for m in MOVS if m["fecha"] <= date(2024, 9, 2)}


def abrir_tramo(j, club, desde, tipo="Profesional", propietario=None):
    t = dict(jugador=j, club=club, desde=desde, hasta=None, tipo=tipo, propietario=propietario)
    TRAMOS.append(t)
    TRAMOS_ABIERTOS[j.id] = t
    return t


def cerrar_tramo(j, hasta):
    t = TRAMOS_ABIERTOS.pop(j.id, None)
    if t:
        t["hasta"] = hasta
    return t


for club, bloque in M.PLANTILLAS_2425.items():
    for nombre, pos, nac, anio, estrella, prop in parsear(bloque):
        j = crear_jugador(nombre, pos, nac, anio, estrella, club)
        llegada = LLEGADAS_VERANO_2024.get(nombre)
        desde = llegada["fecha"] if llegada else date(2024, 7, 1)
        abrir_tramo(j, club, desde, "Cesión" if prop else "Profesional", prop)

INFO_NUEVOS = {n: (p, na, a, e) for n, p, na, a, e, _ in parsear(M.NUEVOS_JUGADORES)}

relegacion_hecha = False
for m in MOVS:
    if m["fecha"] <= date(2024, 9, 2):
        continue
    if not relegacion_hecha and m["fecha"] > date(2025, 6, 30):
        # cierre de los descendidos: sus jugadores dejan de aparecer en LaLiga
        for jid, t in list(TRAMOS_ABIERTOS.items()):
            if t["club"] in M.DESCENDIDOS_2425:
                cerrado = cerrar_tramo(t["jugador"], date(2025, 6, 30))
                cerrado["descenso"] = True
        # ascendidos: plantilla que ya estaba en el club
        for club, bloque in M.PLANTILLAS_ASCENDIDOS_2526.items():
            for nombre, pos, nac, anio, estrella, prop in parsear(bloque):
                j = crear_jugador(nombre, pos, nac, anio, estrella, club)
                abrir_tramo(j, club, date(2025, 7, 1))
        relegacion_hecha = True

    nombre = m["jugador"]
    if nombre in POR_NOMBRE:
        j = buscar(nombre)
    else:
        p, na, a, e = INFO_NUEVOS[nombre]
        j = crear_jugador(nombre, p, na, a, e, m["destino"] if m["destino"] in M.CLUBES else "RSO")
    cerrado = cerrar_tramo(j, m["fecha"] - timedelta(days=1))
    if cerrado:
        cerrado["cierre"] = m["tipo"]
    if m["destino"] in M.CLUBES:
        if m["tipo"] == "Cesión":
            abrir_tramo(j, m["destino"], m["fecha"], "Cesión", m["origen"])
        else:
            abrir_tramo(j, m["destino"], m["fecha"])

for jid, t in list(TRAMOS_ABIERTOS.items()):
    t["hasta"] = FIN_DATOS
TRAMOS_ABIERTOS.clear()

# comprobación: nadie está en dos clubes a la vez
for j in JUGADORES:
    ts = sorted([t for t in TRAMOS if t["jugador"] is j], key=lambda t: t["desde"])
    for a, b in zip(ts, ts[1:]):
        assert a["hasta"] < b["desde"], (j.nombre, a, b)


def club_en(j, dia):
    for t in TRAMOS_J[j.id]:
        if t["desde"] <= dia <= t["hasta"]:
            return t["club"]
    return None


TRAMOS_J = {}
for t in TRAMOS:
    TRAMOS_J.setdefault(t["jugador"].id, []).append(t)


def rendimiento(j, dia):
    e = edad(j.fnac, dia)
    aj = 0.0
    if e > 31:
        aj -= 0.11 * (e - 31)
    if e < 21:
        aj -= 0.06 * (21 - e)
    return j.q + aj


# ----------------------------------------------------------------------------
# 3. Contratos (uno por tramo + renovaciones) con salario simulado
# ----------------------------------------------------------------------------
CONTRATOS = []


def salario_para(j, club, dia):
    nivel = M.CLUBES[club][5]
    fuerza = M.CLUBES[club][4]
    e = edad(j.fnac, dia)
    sq = j.q - fuerza + 0.045 * max(0, e - 27) + j.sesgo_salario
    s = nivel * math.exp(0.85 * sq) * 1_000_000
    if e < 21:
        s *= 0.45
    s = min(max(s, 300_000), 26_000_000)
    return int(round(s / 10_000) * 10_000)


def clausula_para(salario, club, j):
    if club in ("RMA", "FCB") and j.estrella:
        return 1_000_000_000 if club == "RMA" else 500_000_000
    c = salario * rnd.uniform(9, 28)
    return int(round(max(c, 8_000_000) / 1_000_000) * 1_000_000)


num_contrato = 0


def nuevo_contrato(j, club, inicio, fin_prev, baja, tipo, prop, salario, motivo, cierre=None):
    global num_contrato
    num_contrato += 1
    CONTRATOS.append(dict(
        id_contrato=f"CT-{num_contrato:05d}", jugador=j, club=club, inicio=inicio,
        fin_prevista=fin_prev, baja=baja, tipo=tipo, propietario=prop, salario=salario,
        clausula=None if tipo == "Cesión" else clausula_para(salario, club, j), motivo=motivo, cierre=cierre))


for t in sorted(TRAMOS, key=lambda t: t["desde"]):
    j, club = t["jugador"], t["club"]
    # inicio "real" del contrato
    if t["desde"] == date(2024, 7, 1) and t["jugador"].nombre not in LLEGADAS_VERANO_2024 and t["tipo"] == "Profesional":
        anios_atras = rnd.choice([0, 1, 1, 2, 2, 3, 4, 5])
        inicio = date(2024 - anios_atras, 7, 1)
    elif t["desde"] == date(2025, 7, 1) and club in M.ASCENDIDOS_2526 and t["tipo"] == "Profesional" \
            and not any(m["jugador"] == j.nombre and m["destino"] == club for m in MOVS):
        inicio = date(2025 - rnd.choice([1, 1, 2, 3]), 7, 1)
    else:
        inicio = t["desde"]
    if t["tipo"] == "Cesión":
        fin_prev = date(inicio.year + (1 if inicio.month >= 7 else 0), 6, 30)
    else:
        fin_prev = date(inicio.year + rnd.choice([2, 3, 3, 4, 5]) + (1 if inicio.month >= 7 else 0), 6, 30)
        if fin_prev < date(2025, 6, 30):
            fin_prev = date(2025, 6, 30) if rnd.random() < 0.35 else date(rnd.choice([2026, 2027, 2028]), 6, 30)
        if fin_prev <= t["hasta"] and t["hasta"] < FIN_DATOS:
            fin_prev = t["hasta"]       # se le acabó el contrato y se fue libre
    sal = salario_para(j, club, inicio)
    # renovaciones dentro del tramo
    cursor_inicio, cursor_fin, cursor_sal = inicio, fin_prev, sal
    while True:
        renovar_por_fin = cursor_fin < t["hasta"]
        renovar_anticipada = (not renovar_por_fin and t["tipo"] == "Profesional"
                              and rnd.random() < 0.10 and (t["hasta"] - max(cursor_inicio, date(2024, 9, 1))).days > 200)
        if renovar_por_fin:
            f_ren = cursor_fin + timedelta(days=1)
        elif renovar_anticipada:
            ini = max(cursor_inicio, date(2024, 9, 1)) + timedelta(days=60)
            f_ren = ini + timedelta(days=rnd.randint(0, max(1, (t["hasta"] - ini).days - 120)))
        else:
            if t.get("descenso") and cursor_fin > t["hasta"]:
                baja = None          # sigue en el club, pero en Segunda: fuera de nuestro alcance
            elif t["hasta"] == FIN_DATOS and cursor_fin > FIN_DATOS:
                baja = None
            else:
                baja = t["hasta"]
            nuevo_contrato(j, club, cursor_inicio, cursor_fin, baja, t["tipo"], t["propietario"], cursor_sal, "",
                           t.get("cierre"))
            break
        nuevo_contrato(j, club, cursor_inicio, cursor_fin, f_ren - timedelta(days=1),
                       t["tipo"], t["propietario"], cursor_sal, "Renovado")
        cursor_inicio = f_ren
        cursor_fin = date(f_ren.year + rnd.choice([2, 3, 4, 5]), 6, 30)
        subida = rnd.uniform(1.05, 1.6)
        if edad(j.fnac, f_ren) < 21:
            subida = rnd.uniform(1.8, 3.5)      # el canterano que explota y renueva
        cursor_sal = int(round(min(cursor_sal * subida, 26_000_000) / 10_000) * 10_000)


def salario_vigente(j, dia):
    for c in CONTRATOS:
        if c["jugador"] is j and c["inicio"] <= dia and (c["baja"] or c["fin_prevista"]) >= dia:
            return c["salario"]
    return None


# ----------------------------------------------------------------------------
# 4. Lesiones
# ----------------------------------------------------------------------------
TIPOS_LESION = [
    # tipo, zonas, dias_min, dias_max, peso, es_muscular
    ("Sobrecarga muscular", ["Isquiotibiales", "Gemelo", "Cuádriceps", "Aductor"], 4, 12, 26, True),
    ("Rotura fibrilar grado I", ["Isquiotibiales", "Gemelo", "Cuádriceps", "Aductor", "Sóleo"], 14, 28, 20, True),
    ("Rotura fibrilar grado II", ["Isquiotibiales", "Cuádriceps", "Gemelo", "Aductor"], 28, 55, 9, True),
    ("Esguince de tobillo", ["Tobillo"], 10, 35, 12, False),
    ("Contusión", ["Rodilla", "Muslo", "Costillas", "Pie"], 3, 10, 10, False),
    ("Tendinitis rotuliana", ["Rodilla"], 10, 30, 5, False),
    ("Lumbalgia", ["Espalda"], 5, 16, 5, False),
    ("Pubalgia", ["Pubis"], 20, 50, 4, False),
    ("Esguince de rodilla (ligamento lateral interno)", ["Rodilla"], 21, 45, 4, False),
    ("Fractura del quinto metatarsiano", ["Pie"], 50, 85, 1.2, False),
    ("Conmoción cerebral", ["Cabeza"], 7, 12, 1.2, False),
    ("Lesión de menisco", ["Rodilla"], 30, 60, 1.6, False),
]

LESIONES = []
for (nom, fl, fa, tipo, zona, lado) in M.LESIONES_REALES:
    j = POR_NOMBRE[nom][0]
    LESIONES.append(dict(jugador=j, inicio=d(fl), alta=d(fa), tipo=tipo, zona=zona, lado=lado, real=True))

for t in TRAMOS:
    j = t["jugador"]
    for (temp, _v, _c, ini_v, fin_v) in TEMPORADAS:
        a, b = max(t["desde"], ini_v), min(t["hasta"], fin_v)
        dias = (b - a).days
        if dias < 20:
            continue
        e = edad(j.fnac, a)
        lam = 0.95 * (1 + max(0, e - 28) * 0.07) * dias / 320
        n = poisson(lam)
        prev = None
        for _ in range(n):
            if prev and prev["muscular"] and rnd.random() < 0.38:
                tipo, zonas, dmin, dmax, _w, musc = next(x for x in TIPOS_LESION if x[0] == prev["tipo"])
                zona = prev["zona"]
                inicio = prev["alta"] + timedelta(days=rnd.randint(5, 50))
            else:
                tipo, zonas, dmin, dmax, _w, musc = rnd.choices(TIPOS_LESION, weights=[x[4] for x in TIPOS_LESION])[0]
                zona = rnd.choice(zonas)
                inicio = a + timedelta(days=rnd.randint(0, dias))
            dur = rnd.randint(dmin, dmax)
            alta = inicio + timedelta(days=dur)
            if inicio > b:
                continue
            solapa = any(l["jugador"] is j and not (alta < l["inicio"] or inicio > l["alta"]) for l in LESIONES)
            if solapa:
                continue
            les = dict(jugador=j, inicio=inicio, alta=alta, tipo=tipo, zona=zona,
                       lado=rnd.choice(["derecho", "izquierdo"]), real=False, muscular=musc)
            LESIONES.append(les)
            prev = les

LESIONES.sort(key=lambda l: (l["inicio"], l["jugador"].id))
LES_J = {}
for l in LESIONES:
    LES_J.setdefault(l["jugador"].id, []).append(l)


def lesionado(j, dia):
    return any(l["inicio"] <= dia < l["alta"] for l in LES_J.get(j.id, []))


# ----------------------------------------------------------------------------
# 5. Calendario y simulación de partidos
# ----------------------------------------------------------------------------
def calendario(clubes):
    eq = clubes[:]
    rnd.shuffle(eq)
    n = len(eq)
    rondas = []
    for r in range(n - 1):
        jornada = []
        for i in range(n // 2):
            a, b = eq[i], eq[n - 1 - i]
            jornada.append((a, b) if (r + i) % 2 == 0 else (b, a))
        rondas.append(jornada)
        eq = [eq[0]] + [eq[-1]] + eq[1:-1]
    vuelta = [[(b, a) for (a, b) in j] for j in rondas]
    return rondas + vuelta


FORMACIONES = {"4-3-3": (4, 3, 3), "4-4-2": (4, 4, 2), "4-2-3-1": (4, 5, 1), "5-3-2": (5, 3, 2)}


def estadio_de(local, dia):
    if local == "FCB":
        if dia < date(2025, 7, 1):
            return "MONTJUIC"
        return "JOHANCRUYFF" if dia < date(2025, 11, 22) else "CAMPNOU"
    return M.CLUBES[local][3]


def alineacion(club, dia):
    disp = [j for j in JUGADORES if club_en(j, dia) == club and not lesionado(j, dia) and rnd.random() > 0.04]
    sc = {j.id: rendimiento(j, dia) + rnd.gauss(0, 0.42) for j in disp}
    form = rnd.choices(list(FORMACIONES), weights=[5, 3, 4, 1])[0]
    nd, nm, nf = FORMACIONES[form]
    por_pos = {p: sorted([j for j in disp if j.pos == p], key=lambda j: -sc[j.id]) for p in ("POR", "DEF", "MED", "DEL")}
    tit = []
    tit += por_pos["POR"][:1]
    tit += por_pos["DEF"][:nd]
    tit += por_pos["MED"][:nm]
    tit += por_pos["DEL"][:nf]
    resto = sorted([j for j in disp if j not in tit and j.pos != "POR"], key=lambda j: -sc[j.id])
    while len(tit) < 11 and resto:
        tit.append(resto.pop(0))
    banquillo = resto[:9]
    return tit, banquillo


def media(xs):
    return sum(xs) / len(xs) if xs else 0


PARTIDOS = []
STATS = []
id_partido = 0
PESO_GOL = {"POR": 0.0, "DEF": 0.2, "MED": 0.55, "DEL": 2.6}
PESO_ASI = {"POR": 0.02, "DEF": 0.55, "MED": 1.4, "DEL": 1.0}

for (temp, viernes1, clubes, _a, _b) in TEMPORADAS:
    jornadas = calendario(clubes)
    semana = 0
    for nj, partidos in enumerate(jornadas, start=1):
        if nj in (19, 29):
            semana += 1        # parón (Navidad / selecciones)
        viernes = viernes1 + timedelta(days=7 * semana)
        semana += 1
        for (loc, vis) in partidos:
            id_partido += 1
            dia = viernes + timedelta(days=rnd.choice([0, 1, 1, 1, 2, 2, 2, 3]))
            hora = rnd.choice(["14:00", "16:15", "18:30", "18:30", "21:00", "21:00"])
            tl, bl = alineacion(loc, dia)
            tv, bv = alineacion(vis, dia)

            def fuerza(tit):
                att = media([rendimiento(j, dia) for j in tit if j.pos in ("MED", "DEL")])
                dfn = media([rendimiento(j, dia) for j in tit if j.pos in ("POR", "DEF")])
                return att, dfn
            al, dl = fuerza(tl)
            av, dv = fuerza(tv)
            gl = poisson(1.28 * math.exp(0.5 * (al - dv)))
            gv = poisson(0.98 * math.exp(0.5 * (av - dl)))

            est = estadio_de(loc, dia)
            nom_est, ciudad_est, aforo = M.ESTADIOS[est]
            atractivo = 0.78 + 0.08 * M.CLUBES[vis][4] + 0.05 * M.CLUBES[loc][4] + (0.05 if dia.weekday() >= 5 else 0)
            espect = int(aforo * min(0.99, max(0.45, atractivo + rnd.gauss(0, 0.06))))

            PARTIDOS.append(dict(id=id_partido, temporada=temp, jornada=nj, fecha=dia, hora=hora,
                                 local=loc, visitante=vis, estadio=est, goles_local=gl, goles_visitante=gv,
                                 espectadores=espect, arbitro=rnd.choice(M.ARBITROS)))

            for (club, rival, tit, banq, gf, gc, es_local) in ((loc, vis, tl, bl, gl, gv, True), (vis, loc, tv, bv, gv, gl, False)):
                minutos = {j.id: 90 for j in tit}
                titular = {j.id: True for j in tit}
                nsubs = rnd.choices([3, 4, 5], weights=[3, 4, 5])[0]
                candidatos = banq[:]
                for _ in range(min(nsubs, len(candidatos))):
                    entra = candidatos.pop(0) if rnd.random() < 0.7 else candidatos.pop(rnd.randrange(len(candidatos)))
                    sale_opc = [j for j in tit if j.pos == entra.pos and minutos[j.id] == 90] or \
                               [j for j in tit if j.pos != "POR" and minutos[j.id] == 90]
                    if not sale_opc:
                        break
                    sale = rnd.choice(sale_opc)
                    m_cambio = rnd.randint(46, 88)
                    minutos[sale.id] = m_cambio
                    minutos[entra.id] = 90 - m_cambio
                    titular[entra.id] = False
                en_campo = [j for j in tit] + [j for j in banq if j.id in minutos]
                goles = {j.id: 0 for j in en_campo}
                asis = {j.id: 0 for j in en_campo}
                for _ in range(gf):
                    pes = [PESO_GOL[j.pos] * math.exp(0.6 * rendimiento(j, dia) + j.remate) * minutos[j.id] / 90 for j in en_campo]
                    if sum(pes) == 0:
                        continue
                    g = elegir_ponderado(en_campo, pes)
                    goles[g.id] += 1
                    if rnd.random() < 0.74:
                        otros = [j for j in en_campo if j is not g]
                        pa = [PESO_ASI[j.pos] * math.exp(0.6 * rendimiento(j, dia)) * minutos[j.id] / 90 for j in otros]
                        a = elegir_ponderado(otros, pa)
                        asis[a.id] += 1
                res = 1 if gf > gc else (0 if gf == gc else -1)
                for j in en_campo:
                    mins = minutos[j.id]
                    if mins <= 0:
                        continue
                    r = rendimiento(j, dia)
                    amar = 1 if rnd.random() < {"POR": 0.04, "DEF": 0.16, "MED": 0.15, "DEL": 0.08}[j.pos] * mins / 90 else 0
                    roja = 1 if rnd.random() < 0.006 else 0
                    tiros = goles[j.id] + poisson({"POR": 0.0, "DEF": 0.35, "MED": 0.8, "DEL": 1.9}[j.pos] * mins / 90 * math.exp(0.3 * r))
                    a_puerta = goles[j.id] + (rnd.randint(0, tiros - goles[j.id]) if tiros > goles[j.id] else 0)
                    pi = int({"POR": 30, "DEF": 52, "MED": 58, "DEL": 26}[j.pos] * mins / 90 * rnd.uniform(0.7, 1.3) * (1 + 0.15 * r))
                    pct = min(0.95, max(0.55, 0.78 + 0.05 * r + rnd.gauss(0, 0.05)))
                    recup = poisson({"POR": 1.0, "DEF": 5.5, "MED": 5.0, "DEL": 2.0}[j.pos] * mins / 90)
                    if j.pos == "POR":
                        val = 6.6 - 0.45 * gc + 0.3 * r + (0.6 if gc == 0 else 0) + rnd.gauss(0, 0.45)
                    else:
                        val = 6.3 + 0.95 * goles[j.id] + 0.6 * asis[j.id] + 0.28 * r + 0.25 * res + rnd.gauss(0, 0.45) - 1.2 * roja
                    if mins < 25:
                        val = 6.0 + (val - 6.0) * 0.4
                    val = round(min(10, max(3.5, val)), 1)
                    STATS.append(dict(id_partido=id_partido, temporada=temp, fecha=dia, jugador=j, club=club, rival=rival,
                                      local=es_local, titular=titular[j.id], minutos=mins, goles=goles[j.id],
                                      asistencias=asis[j.id], tiros=tiros, tiros_puerta=a_puerta, pases_int=pi,
                                      pases_comp=int(pi * pct), recuperaciones=recup, amarillas=amar, rojas=roja,
                                      valoracion=val))


# partidos perdidos por lesión
PART_CLUB = {}
for p in PARTIDOS:
    PART_CLUB.setdefault(p["local"], []).append(p["fecha"])
    PART_CLUB.setdefault(p["visitante"], []).append(p["fecha"])
for l in LESIONES:
    perdidos = 0
    for f in sorted(set(PART_CLUB.get(club_en(l["jugador"], l["inicio"]) or "", []))):
        if l["inicio"] <= f < l["alta"]:
            perdidos += 1
    l["partidos_perdidos"] = perdidos


# ----------------------------------------------------------------------------
# 6. Textos: partes médicos e informes de scouting
# ----------------------------------------------------------------------------
MECANISMO = ["en una acción de sprint durante el partido", "en el entrenamiento de la mañana",
             "tras un golpe fortuito con un rival", "al realizar un cambio de ritmo",
             "en un lance del juego sin contacto", "durante la sesión de recuperación",
             "al caer mal tras un salto", "en el calentamiento previo al partido"]
PRUEBA = ["Las pruebas de imagen (resonancia magnética) confirman", "La ecografía realizada hoy confirma",
          "Las pruebas médicas confirman", "La exploración clínica y la resonancia confirman"]


def parte_medico(l, previas):
    j = l["jugador"]
    recurrente = [p for p in previas if p["zona"] == l["zona"] and (l["inicio"] - p["alta"]).days < 200]
    dias = (l["alta"] - l["inicio"]).days
    zona = l["zona"].lower()
    femenino = zona in ("rodilla", "espalda", "cabeza", "costillas")
    plural = zona in ("isquiotibiales", "costillas")
    art = ("las " if femenino else "los ") if plural else ("la " if femenino else "el ")
    lado = "" if zona in ("espalda", "cabeza", "pubis") else " " + (l["lado"].replace("o", "a") if femenino else l["lado"]) + ("s" if plural else "")
    if femenino and not plural:
        lado = lado.replace("derecho", "derecha").replace("izquierdo", "izquierda")
    tipo_l = l["tipo"][0].lower() + l["tipo"][1:]
    indef = "un " if tipo_l.startswith("esguince") else "una "
    if zona in tipo_l:
        txt = [f"{rnd.choice(PRUEBA)} que {j.nombre} sufre {indef}{tipo_l}{lado}."]
    else:
        txt = [f"{rnd.choice(PRUEBA)} que {j.nombre} sufre {indef}{tipo_l} en {art}{zona}{lado}."]
    if l["real"]:
        txt = [f"{j.nombre} ha sido operado con éxito de una {l['tipo'].lower()} de la rodilla {l['lado']}. "
               f"Se trata de una lesión de larga duración que le apartará de los terrenos de juego gran parte de la temporada."]
    else:
        txt.append(f"La lesión se produjo {rnd.choice(MECANISMO)}.")
    if recurrente:
        txt.append(rnd.choice([
            "Es la segunda lesión en la misma zona en pocos meses, por lo que se considera una recaída y se extremarán las precauciones.",
            "Recae de la lesión sufrida anteriormente en esta misma zona; el cuerpo médico estudiará un plan de readaptación específico.",
            "Se trata de una lesión recurrente: el jugador ya había tenido problemas en esa misma zona esta temporada.",
        ]))
    if dias >= 45:
        txt.append(rnd.choice([
            "Se trata de una lesión grave y el tiempo de baja será largo.",
            "El pronóstico es de baja prolongada; su recuperación será lenta.",
            f"Estará de baja en torno a {dias // 7} semanas, una lesión de gravedad importante.",
        ]))
    elif dias >= 15:
        txt.append(rnd.choice([
            f"El tiempo estimado de baja es de unas {max(2, dias // 7)} semanas.",
            "Su evolución marcará su disponibilidad; se estima una baja de varias semanas.",
        ]))
    else:
        txt.append(rnd.choice([
            "Es una lesión leve; se espera que pueda volver a entrenar con el grupo en pocos días.",
            "Pronóstico leve. Será baja para el próximo partido como precaución.",
            "No reviste gravedad. Se le tratará con fisioterapia y se valorará día a día.",
        ]))
    if rnd.random() < 0.12 and not l["real"]:
        txt.append("Pendiente de nuevas pruebas para confirmar el alcance.")
    return " ".join(txt), bool(recurrente), dias >= 45


FRASES = {
    "tec": {
        "alto": ["Técnicamente es muy fino: controla orientado y casi nunca pierde el balón bajo presión.",
                 "Tiene un golpeo excelente y una calidad en el último pase que marca diferencias.",
                 "Su primer control es de otro nivel; juega a uno o dos toques con mucha limpieza."],
        "medio": ["Técnicamente correcto, sin grandes alardes.",
                  "Cumple con balón, aunque abusa del pase de seguridad.",
                  "Buen golpeo en estático, le cuesta más en conducción."],
        "bajo": ["Le cuesta mucho el control en espacios reducidos.",
                 "Pierde demasiados balones en zona de creación.",
                 "Técnicamente está por debajo del nivel que pedimos para el primer equipo."],
    },
    "fis": {
        "alto": ["Físicamente es un portento: llega al minuto 90 apretando igual que en el primero.",
                 "Muy potente en los duelos y con una zancada que rompe líneas.",
                 "Gran despliegue físico, cubre muchísimo campo."],
        "medio": ["Condición física normal para la categoría.",
                  "Sin problemas físicos aparentes, aunque bajó el ritmo en la segunda parte.",
                  "Aguanta bien los duelos, sin destacar."],
        "bajo": ["Se le ve justo de forma: a partir del minuto 60 desaparece.",
                 "Pierde la mayoría de duelos y le falta velocidad para competir a este nivel.",
                 "Físicamente sufre mucho ante rivales rápidos."],
    },
    "tac": {
        "alto": ["Lee el juego como pocos y siempre está bien posicionado.",
                 "Muy inteligente tácticamente: interpreta cuándo apretar y cuándo temporizar.",
                 "Entiende perfectamente los movimientos de ruptura y los espacios."],
        "medio": ["Tácticamente cumple, aunque a veces se descuelga.",
                  "Ordenado, sigue el plan del entrenador sin aportar mucho más.",
                  "Comete algún error de posicionamiento, nada grave."],
        "bajo": ["Tácticamente desordenado; deja muchos espacios a su espalda.",
                 "Se pierde en las transiciones defensivas y llega tarde a las coberturas.",
                 "Toma malas decisiones con frecuencia."],
    },
    "men": {
        "alto": ["Personalidad de líder; pide el balón en los momentos difíciles.",
                 "Muy competitivo y con carácter, contagia al resto.",
                 "Mentalmente fuerte, no se esconde nunca."],
        "medio": ["Actitud correcta durante todo el partido.",
                  "Compromiso bueno, sin ser un líder.",
                  "Se frustró un poco tras el gol rival pero se repuso."],
        "bajo": ["Se desconecta del partido con facilidad.",
                 "Protesta mucho y pierde la concentración.",
                 "Le falta carácter cuando el partido se complica."],
    },
}
POS_FRASE = {
    "POR": {"alto": "Seguro por alto y con muy buenos reflejos bajo palos.", "medio": "Correcto en las paradas, dudoso en alguna salida.", "bajo": "Muy inseguro en las salidas y con el juego de pies."},
    "DEF": {"alto": "Contundente en el uno contra uno y saca el balón jugado con criterio.", "medio": "Defensivamente cumple, le falta salida de balón.", "bajo": "Sufre muchísimo en el uno contra uno."},
    "MED": {"alto": "Da sentido al juego del equipo y filtra pases entre líneas.", "medio": "Mueve el balón con criterio pero sin profundidad.", "bajo": "No consigue conectar con los de arriba."},
    "DEL": {"alto": "Definición de primer nivel: no necesita muchas ocasiones para marcar.", "medio": "Trabaja mucho para el equipo pero le falta gol.", "bajo": "Muy poco acierto de cara a puerta."},
}
CIERRE = {
    "Fichar": ["Lo ficharía sin dudarlo si la operación encaja económicamente.",
               "Prioridad alta para la próxima ventana de mercado.",
               "Es exactamente el perfil que buscamos. Recomiendo iniciar contactos ya.",
               "Jugador diferencial. Hay que moverse antes de que suba su precio.",
               "Mi recomendación es clara: adelante con la operación."],
    "Seguir observando": ["Merece la pena seguirle unos partidos más antes de decidir.",
                          "Interesante, pero necesito verle contra rivales de más nivel.",
                          "Perfil a vigilar. Volveré a verle en las próximas semanas.",
                          "Tiene cosas buenas, pero hay dudas. Mantener en seguimiento.",
                          "Hoy no es suficiente para tomar una decisión."],
    "Descartar": ["No aporta nada diferencial respecto a lo que ya tenemos.",
                  "No lo recomiendo.",
                  "Descartado: la relación calidad-precio no compensa.",
                  "No es jugador para nosotros, no seguiría invirtiendo tiempo en él.",
                  "Por edad y rendimiento, no tiene sentido plantear su fichaje."],
}
CIERRE_CORTO = {"Fichar": ["FICHAR.", "Prioridad alta.", "Ir a por él."],
                "Seguir observando": ["Seguir.", "Ver más partidos.", "Dudas. Seguir."],
                "Descartar": ["Descartar.", "No interesa.", "No."]}
POSICIONES_ESPECIFICAS = {
    "POR": ["Portero"],
    "DEF": ["Lateral derecho", "Lateral izquierdo", "Central", "Carrilero"],
    "MED": ["Pivote", "Interior", "Mediapunta", "Extremo derecho", "Extremo izquierdo"],
    "DEL": ["Delantero centro", "Extremo izquierdo", "Extremo derecho", "Segundo delantero"],
}


def nivel(x):
    return "alto" if x > 0.55 else ("bajo" if x < -0.25 else "medio")


INFORMES = []
ETIQUETAS = []
STATS_POR_PARTIDO = {}
for s in STATS:
    STATS_POR_PARTIDO.setdefault(s["id_partido"], []).append(s)
LES_ANT = {}

num_inf = 0
for ojeador in M.OJEADORES:
    nombre_oj, email_oj, zona, estilo = ojeador
    sesgo_oj = rnd.gauss(0, 0.15)
    for p in PARTIDOS:
        if zona != "Todas" and M.CLUBES[p["local"]][6] != zona:
            continue
        prob = 0.85 if zona != "Todas" else 0.20
        if rnd.random() > prob:
            continue
        candidatos = [s for s in STATS_POR_PARTIDO[p["id"]] if s["minutos"] >= 45]
        if not candidatos:
            continue
        for s in rnd.sample(candidatos, k=rnd.choice([1, 1, 2])):
            j = s["jugador"]
            dia_inf = p["fecha"] + timedelta(days=rnd.randint(0, 3), hours=0)
            e = edad(j.fnac, p["fecha"])
            percep = rendimiento(j, p["fecha"]) - M.CLUBES[s["club"]][4] * 0.25 + 0.55 * (s["valoracion"] - 6.6) + sesgo_oj + rnd.gauss(0, 0.3)
            nota = round(min(9.8, max(3.0, 6.3 + 1.25 * percep)), 1)
            les_prev = [l for l in LES_J.get(j.id, []) if l["alta"] < p["fecha"] and (p["fecha"] - l["alta"]).days < 365]
            historial_malo = len(les_prev) >= 3
            if nota >= 7.6 and e <= 29 and not historial_malo:
                rec = "Fichar"
            elif nota < 6.2 or (e >= 32 and nota < 7.4) or (historial_malo and nota < 7.0):
                rec = "Descartar"
            else:
                rec = "Seguir observando"
            loc_txt, vis_txt = alias(p["local"], "alias"), alias(p["visitante"], "alias")
            aspectos = {k: nivel(percep + rnd.gauss(0, 0.55)) for k in ("tec", "fis", "tac", "men")}
            pos_esp = rnd.sample(POSICIONES_ESPECIFICAS[j.pos], k=min(len(POSICIONES_ESPECIFICAS[j.pos]), rnd.choice([1, 1, 2])))
            nombre_txt = j.nombre if rnd.random() > 0.15 else sin_tildes(j.nombre)
            if estilo == "telegrafico" or (estilo == "mixto" and rnd.random() < 0.4):
                partes = [f"{loc_txt}-{vis_txt}.", f"{s['minutos']}'.",
                          rnd.choice(FRASES["tec"][aspectos["tec"]]).split(":")[0].split(";")[0].rstrip(".") + ".",
                          rnd.choice(FRASES["fis"][aspectos["fis"]]).split(":")[0].rstrip(".") + "."]
                if s["goles"]:
                    partes.append(f"Marcó {s['goles']}.")
                if historial_malo:
                    partes.append("Ojo, muchas lesiones.")
                partes.append(rnd.choice(CIERRE_CORTO[rec]))
                texto = " ".join(partes)
            else:
                partes = [rnd.choice([f"Le vi en el {loc_txt} - {vis_txt} del {p['fecha'].strftime('%d/%m/%Y')}.",
                                      f"Partido observado: {loc_txt} contra {vis_txt}.",
                                      f"Seguimiento en directo del {loc_txt}-{vis_txt}."]),
                          rnd.choice(FRASES["tec"][aspectos["tec"]]),
                          POS_FRASE[j.pos][aspectos["tac"]],
                          rnd.choice(FRASES["fis"][aspectos["fis"]]),
                          rnd.choice(FRASES["tac"][aspectos["tac"]]),
                          rnd.choice(FRASES["men"][aspectos["men"]])]
                if s["goles"]:
                    partes.append(f"Hizo {s['goles']} gol{'es' if s['goles'] > 1 else ''}.")
                if s["asistencias"]:
                    partes.append("Dio una asistencia de mucha calidad.")
                if e <= 22:
                    partes.append(f"Con {e} años tiene muchísimo margen de mejora.")
                elif e >= 32:
                    partes.append(f"Con {e} años su rendimiento ya no es el de antes y su contrato pesa mucho.")
                if historial_malo:
                    partes.append("Me preocupa mucho su historial de lesiones musculares en el último año.")
                partes.append(rnd.choice(CIERRE[rec]))
                texto = " ".join(partes)
            num_inf += 1
            INFORMES.append(dict(id=f"INF-{num_inf:05d}", fecha=datetime.combine(dia_inf, datetime.min.time()) + timedelta(hours=rnd.randint(9, 23), minutes=rnd.choice([0, 15, 30, 45])),
                                 ojeador=ojeador, jugador=j, nombre_txt=nombre_txt, club=s["club"], partido=p,
                                 partido_txt=f"{loc_txt} - {vis_txt}", posiciones=pos_esp, nota=nota, texto=texto))
            ETIQUETAS.append(dict(id_informe=f"INF-{num_inf:05d}", recomendacion_real=rec))

INFORMES.sort(key=lambda x: x["fecha"])


# ----------------------------------------------------------------------------
# 7. Escritura de CSVs con "suciedad" controlada
# ----------------------------------------------------------------------------
def fmt_fecha_es(dd):
    return dd.strftime("%d/%m/%Y")


def fmt_importe_sucio(v):
    r = rnd.random()
    if r < 0.6:
        return str(v)
    if r < 0.8:
        return f"{v:,.0f} €".replace(",", ".")
    if v >= 1_000_000:
        m = v / 1_000_000
        return (f"{m:.1f}".rstrip("0").rstrip(".") + "M").replace(".", ",") if rnd.random() < 0.5 else f"{m:g}M€"
    return str(v)


TABLAS = {}

# RAW_PARTIDOS ----------------------------------------------------------------
cols = ["ID_PARTIDO", "TEMPORADA", "JORNADA", "FECHA_PARTIDO", "HORA", "EQUIPO_LOCAL", "EQUIPO_VISITANTE",
        "ESTADIO", "CIUDAD_ESTADIO", "AFORO_ESTADIO", "GOLES_LOCAL", "GOLES_VISITANTE", "RESULTADO",
        "ESPECTADORES", "ARBITRO", "_FECHA_EXTRACCION"]
filas = []
for p in PARTIDOS:
    nom_est, ciudad_est, aforo = M.ESTADIOS[p["estadio"]]
    fuente_nombre = "corto" if rnd.random() < 0.04 else "oficial"
    filas.append([
        f"LL-{p['id']:05d}", p["temporada"] if rnd.random() > 0.03 else p["temporada"].replace("/", "-20"),
        p["jornada"], fmt_fecha_es(p["fecha"]) if rnd.random() < 0.03 else p["fecha"].isoformat(), p["hora"],
        alias(p["local"], fuente_nombre), alias(p["visitante"], fuente_nombre), nom_est, ciudad_est,
        aforo if rnd.random() > 0.05 else f"{aforo:,}".replace(",", "."),
        p["goles_local"], p["goles_visitante"],
        "1" if p["goles_local"] > p["goles_visitante"] else ("X" if p["goles_local"] == p["goles_visitante"] else "2"),
        "" if rnd.random() < 0.02 else p["espectadores"], p["arbitro"], FECHA_EXTRACCION])
for f in rnd.sample(filas, 7):
    dup = f[:]
    dup[-1] = "2026-07-03 06:00:00"
    filas.append(dup)
filas.sort(key=lambda r: (r[0], r[-1]))
TABLAS["API_LALIGA.PARTIDOS"] = (cols, filas)

# RAW_ESTADISTICAS_JUGADOR_PARTIDO --------------------------------------------
POS_LARGA = {"POR": "Portero", "DEF": "Defensa", "MED": "Centrocampista", "DEL": "Delantero"}
cols = ["ID_PARTIDO", "TEMPORADA", "FECHA_PARTIDO", "ID_JUGADOR_PROVEEDOR", "JUGADOR", "FECHA_NACIMIENTO",
        "NACIONALIDAD", "EQUIPO", "RIVAL", "CONDICION", "POSICION", "TITULAR", "MINUTOS", "GOLES", "ASISTENCIAS",
        "TIROS", "TIROS_A_PUERTA", "PASES_INTENTADOS", "PASES_COMPLETADOS", "RECUPERACIONES",
        "TARJETAS_AMARILLAS", "TARJETAS_ROJAS", "VALORACION", "_FECHA_EXTRACCION"]
filas = []
for s in STATS:
    j = s["jugador"]
    nombre = j.nombre
    r = rnd.random()
    if r < 0.02:
        nombre = nombre.upper()
    elif r < 0.04:
        nombre = f" {nombre} "
    val = s["valoracion"]
    rv = rnd.random()
    val_txt = "" if rv < 0.03 else (str(val).replace(".", ",") if rv < 0.08 else str(val))
    tit = (("S" if s["titular"] else "N") if rnd.random() < 0.5 else ("true" if s["titular"] else "false"))
    filas.append([f"LL-{s['id_partido']:05d}", s["temporada"], fmt_fecha_es(s["fecha"]), j.id_prov, nombre,
                  fmt_fecha_es(j.fnac), j.nac, alias(s["club"], "corto"), alias(s["rival"], "corto"),
                  "Local" if s["local"] else "Visitante", j.pos, tit, s["minutos"], s["goles"], s["asistencias"],
                  s["tiros"], s["tiros_puerta"], s["pases_int"], s["pases_comp"], s["recuperaciones"],
                  s["amarillas"], s["rojas"], val_txt, FECHA_EXTRACCION])
for f in rnd.sample(filas, 160):
    filas.append(f[:])
rnd.shuffle(filas)
TABLAS["PROVEEDOR_ESTADISTICAS.ESTADISTICAS_JUGADOR_PARTIDO"] = (cols, filas)

# RAW_CONTRATOS ---------------------------------------------------------------
cols = ["ID_CONTRATO", "CODIGO_LICENCIA", "JUGADOR", "FECHA_NACIMIENTO", "NACIONALIDADES", "POSICION", "EQUIPO",
        "CIUDAD_EQUIPO", "TIPO_CONTRATO", "CLUB_PROPIETARIO", "FECHA_INICIO", "FECHA_FIN_PREVISTA", "FECHA_BAJA",
        "ESTADO_CONTRATO", "SALARIO_BRUTO_ANUAL_EUR", "CLAUSULA_RESCISION_EUR", "AGENTE", "AGENCIA_REPRESENTACION",
        "EMAIL_AGENCIA", "_FECHA_EXTRACCION"]
filas = []
for c in sorted(CONTRATOS, key=lambda c: c["id_contrato"]):
    j = c["jugador"]
    nac = M.NACIONALIDAD_DOBLE.get(j.nombre, j.nac)
    if c["motivo"] == "Renovado":
        estado = "Renovado"
    elif c["baja"] is None:
        estado = "Vigente"
    elif c["tipo"] == "Cesión":
        estado = "Cesión finalizada"
    elif c["cierre"] == "Cesión":
        estado = "Cedido a otro club"
    elif c["cierre"] == "Traspaso":
        estado = "Rescindido por traspaso"
    else:
        estado = "Finalizado"
    f_ini = c["inicio"].isoformat() if rnd.random() > 0.1 else fmt_fecha_es(c["inicio"])
    sal = c["salario"] if rnd.random() > 0.06 else f"{c['salario']:,.0f} €".replace(",", ".")
    cla = "" if c["clausula"] is None or rnd.random() < 0.05 else c["clausula"]
    ag_nom, ag_mail, _ = j.agencia
    filas.append([c["id_contrato"], j.licencia, j.nombre, j.fnac.isoformat(), nac, POS_LARGA[j.pos],
                  M.CLUBES[c["club"]][0], M.CLUBES[c["club"]][2], c["tipo"],
                  club_txt(c["propietario"]) if c["propietario"] else "", f_ini, c["fin_prevista"].isoformat(),
                  c["baja"].isoformat() if c["baja"] else "", estado, sal, cla, j.agente, ag_nom, ag_mail,
                  FECHA_EXTRACCION])
TABLAS["RRHH.CONTRATOS"] = (cols, filas)

# RAW_TRASPASOS ---------------------------------------------------------------
cols = ["ID_OPERACION", "FECHA_OPERACION", "VENTANA", "JUGADOR", "NACIONALIDAD", "POSICION", "CLUB_ORIGEN",
        "LIGA_ORIGEN", "PAIS_ORIGEN", "CLUB_DESTINO", "LIGA_DESTINO", "PAIS_DESTINO", "TIPO_OPERACION",
        "IMPORTE", "_FECHA_EXTRACCION"]
filas = []
for i, m in enumerate(MOVS, start=1):
    j = POR_NOMBRE[m["jugador"]][0]
    co, lo, po = club_liga_pais(m["origen"])
    cd, ld, pd = club_liga_pais(m["destino"])
    f = m["fecha"]
    ventana = (f"Verano {f.year}" if 5 <= f.month <= 9 else f"Invierno {f.year if f.month <= 2 else f.year + 1}")
    if m["tipo"] in ("Libre",):
        imp = rnd.choice(["Libre", "0", ""])
    elif m["tipo"] in ("Cesión", "Fin de cesión"):
        imp = rnd.choice(["Cesión", "0", "", "N/D"])
    else:
        imp = fmt_importe_sucio(m["importe"])
    filas.append([f"TR-{i:04d}", fmt_fecha_es(f), ventana, m["jugador"], j.nac, POS_LARGA[j.pos], co, lo, po, cd, ld, pd,
                  m["tipo"], imp, FECHA_EXTRACCION])
TABLAS["MERCADO.TRASPASOS"] = (cols, filas)

# RAW_LESIONES ----------------------------------------------------------------
cols = ["ID_LESION", "CODIGO_LICENCIA", "JUGADOR", "EQUIPO", "TEMPORADA", "FECHA_LESION", "FECHA_ALTA",
        "TIPO_LESION", "ZONA_CORPORAL", "DIAS_BAJA", "PARTIDOS_PERDIDOS", "MEDICO_RESPONSABLE", "PARTE_MEDICO",
        "_FECHA_EXTRACCION"]
filas = []
MEDICO_CLUB = {c: M.MEDICOS[i % len(M.MEDICOS)] for i, c in enumerate(M.CLUBES)}
ETIQ_LES = []
for i, l in enumerate(LESIONES, start=1):
    j = l["jugador"]
    club = club_en(j, l["inicio"])
    if club is None:
        continue
    previas = [x for x in LES_J[j.id] if x["alta"] <= l["inicio"]]
    texto, recurrente, grave = parte_medico(l, previas)
    temp = "2024/25" if l["inicio"] < date(2025, 7, 1) else "2025/26"
    zona = l["zona"] if rnd.random() > 0.08 else rnd.choice([l["zona"].upper(), l["zona"].lower()])
    filas.append([f"LES-{i:05d}", j.licencia, j.nombre if rnd.random() > 0.1 else sin_tildes(j.nombre),
                  alias(club, "alias"), temp, fmt_fecha_es(l["inicio"]),
                  "" if rnd.random() < 0.03 else fmt_fecha_es(l["alta"]), l["tipo"], zona,
                  (l["alta"] - l["inicio"]).days, l["partidos_perdidos"], MEDICO_CLUB[club], texto, FECHA_EXTRACCION])
    ETIQ_LES.append(dict(id_lesion=f"LES-{i:05d}", es_recurrente_real=recurrente, es_grave_real=grave))
TABLAS["SERVICIOS_MEDICOS.LESIONES"] = (cols, filas)

# RAW_INFORMES_SCOUTING -------------------------------------------------------
cols = ["ID_INFORME", "FECHA_INFORME", "OJEADOR", "EMAIL_OJEADOR", "ZONA_OJEADOR", "JUGADOR", "EQUIPO_JUGADOR",
        "PARTIDO_OBSERVADO", "FECHA_PARTIDO", "POSICIONES_OBSERVADAS", "NOTA_GLOBAL", "INFORME", "_FECHA_EXTRACCION"]
filas = []
for inf in INFORMES:
    oj = inf["ojeador"]
    nota = str(inf["nota"]) if oj[3] != "mixto" else str(inf["nota"]).replace(".", ",")
    filas.append([inf["id"], inf["fecha"].strftime("%Y-%m-%d %H:%M"), oj[0], oj[1], oj[2], inf["nombre_txt"],
                  alias(inf["club"], "alias"), inf["partido_txt"], inf["partido"]["fecha"].isoformat(),
                  ", ".join(inf["posiciones"]), nota, inf["texto"], FECHA_EXTRACCION])
TABLAS["APP_SCOUTING.INFORMES_SCOUTING"] = (cols, filas)


# ----------------------------------------------------------------------------
# 8. Guardar
# ----------------------------------------------------------------------------
# Convención del curso: database {ENV}_BRONZE_DB, un esquema por sistema de origen.
# Fichero CSV: <esquema>__<tabla>.csv (todos en la misma carpeta y en la raíz del stage).
def fichero(nombre):
    esq, tab = nombre.split(".")
    return f"{esq.lower()}__{tab.lower()}.csv"


DIR_BRONZE.mkdir(parents=True, exist_ok=True)
DIR_VALID.mkdir(parents=True, exist_ok=True)
DIR_SQL.mkdir(parents=True, exist_ok=True)
for viejo in DIR_BRONZE.glob("raw_*.csv"):
    viejo.unlink()

for nombre, (cols, filas) in TABLAS.items():
    with open(DIR_BRONZE / fichero(nombre), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        w.writerows(filas)

with open(DIR_VALID / "etiquetas_scouting.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["id_informe", "recomendacion_real"])
    w.writeheader()
    w.writerows(ETIQUETAS)
with open(DIR_VALID / "etiquetas_lesiones.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["id_lesion", "es_recurrente_real", "es_grave_real"])
    w.writeheader()
    w.writerows(ETIQ_LES)

# SQL de carga generado a partir de las mismas columnas (así nunca se desincronizan)
ESQUEMAS = sorted({n.split(".")[0] for n in TABLAS})
sql = ["""-- =============================================================================
-- 02_bronze_laliga.sql   (GENERADO por scripts/generar_bronze.py - no editar a mano)
-- Requisito: haber ejecutado antes el script del profesor (01 · Entorno Snowflake del
-- curso), que crea WH_CURSO, las databases {ENV}_BRONZE/SILVER/GOLD_DB y los roles
-- {ENV}_TRANSFORM_ROLE.
--
-- Qué hace:
--   1. Crea en DEV_BRONZE_DB un esquema por sistema de origen (convención del curso).
--   2. Crea un stage interno y un file format CSV.
--   3. Crea las 6 tablas (TODAS las columnas VARCHAR + metadatos de carga) y las carga
--      con COPY INTO.
--   4. Da permiso de lectura a DEV_TRANSFORM_ROLE (dbt) y acceso a Cortex AI.
-- Bronze solo existe en DEV: PRE y PRO serán clones (script 03 del curso).
-- =============================================================================
USE ROLE SYSADMIN;
USE WAREHOUSE WH_CURSO;
USE DATABASE DEV_BRONZE_DB;

-- 1. Un esquema por fuente
""" + "".join(f"CREATE SCHEMA IF NOT EXISTS DEV_BRONZE_DB.{e};\n" for e in ESQUEMAS) + """
-- 2. File format y stage (en PUBLIC: es infraestructura de carga, no datos)
CREATE OR REPLACE FILE FORMAT DEV_BRONZE_DB.PUBLIC.FF_CSV_RAW
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('')
  EMPTY_FIELD_AS_NULL = TRUE
  ENCODING = 'UTF8';

CREATE STAGE IF NOT EXISTS DEV_BRONZE_DB.PUBLIC.STG_LALIGA
  FILE_FORMAT = DEV_BRONZE_DB.PUBLIC.FF_CSV_RAW
  COMMENT = 'CSV recibidos de las 6 fuentes del proyecto LaLiga';

-- >>> PARA AQUÍ y sube los 6 CSV de data/bronze/ al stage:
--     Snowsight: Data > Databases > DEV_BRONZE_DB > PUBLIC > Stages > STG_LALIGA > "+ Files"
--     (o con SnowSQL: PUT file://data/bronze/*.csv @DEV_BRONZE_DB.PUBLIC.STG_LALIGA;)
LIST @DEV_BRONZE_DB.PUBLIC.STG_LALIGA;

-- 3. Tablas y carga
"""]
for nombre, (cols, _f) in TABLAS.items():
    defs = ",\n  ".join(f"{c} VARCHAR" for c in cols)
    sql.append(f"""
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE DEV_BRONZE_DB.{nombre} (
  {defs},
  _FICHERO_ORIGEN VARCHAR,
  _FECHA_CARGA TIMESTAMP_NTZ
);
COPY INTO DEV_BRONZE_DB.{nombre}
FROM (
  SELECT {", ".join(f"${i}" for i in range(1, len(cols) + 1))},
         METADATA$FILENAME, CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
  FROM @DEV_BRONZE_DB.PUBLIC.STG_LALIGA/{fichero(nombre)}
)
FILE_FORMAT = (FORMAT_NAME = DEV_BRONZE_DB.PUBLIC.FF_CSV_RAW)
ON_ERROR = 'ABORT_STATEMENT';
""")
sql.append("""
-- 4. Permisos: dbt (DEV_TRANSFORM_ROLE) lee bronze; nunca escribe en él
GRANT USAGE ON DATABASE DEV_BRONZE_DB TO ROLE DEV_TRANSFORM_ROLE;
""" + "".join(f"""GRANT USAGE ON SCHEMA DEV_BRONZE_DB.{e} TO ROLE DEV_TRANSFORM_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA DEV_BRONZE_DB.{e} TO ROLE DEV_TRANSFORM_ROLE;
""" for e in ESQUEMAS) + """
-- Cortex AI (AI_COMPLETE, AI_CLASSIFY, AI_FILTER) para la capa GOLD.
-- Por defecto CORTEX_USER ya está concedido a PUBLIC; esto lo hace explícito.
USE ROLE ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE DEV_TRANSFORM_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE PRE_TRANSFORM_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE PRO_TRANSFORM_ROLE;
-- Si tu región no tiene el modelo que usemos:
-- ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
USE ROLE SYSADMIN;

-- 5. Comprobación de volúmenes
""")
sql.append("\nUNION ALL ".join(f"SELECT '{n}' AS tabla, COUNT(*) AS filas FROM DEV_BRONZE_DB.{n}" for n in TABLAS) + ";\n")
for viejo in ("01_bronze_ddl_y_carga.sql", "00_usuario_dbt.sql"):
    if (DIR_SQL / viejo).exists():
        (DIR_SQL / viejo).unlink()
(DIR_SQL / "02_bronze_laliga.sql").write_text("".join(sql), encoding="utf-8")

# resumen
print("Jugadores:", len(JUGADORES), "| Tramos:", len(TRAMOS))
for n, (c, f) in TABLAS.items():
    print(f"{n:55s} {len(f):>7} filas  {len(c)} columnas")
