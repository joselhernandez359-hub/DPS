from flask import Flask, render_template, request, Response
import matplotlib.pyplot as plt
import io, math
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# ======================================================
# MENÚ
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")

# ======================================================
# DESTILACIÓN McCABE–THIELE (WEB)
# ======================================================
@app.route("/destilacion_mccabe", methods=["GET", "POST"])
def destilacion_mccabe():

    if request.method == "GET":
        return render_template("destilacion_mccabe.html")

    # =========================
    # ENTRADA DE DATOS
    # =========================
    T_low = float(request.form["T_low"])
    T_high = float(request.form["T_high"])
    P_op = float(request.form["P_op"])
    n_div = int(request.form["n_div"])

    A1 = float(request.form["A1"])
    B1 = float(request.form["B1"])
    C1 = float(request.form["C1"])

    A2 = float(request.form["A2"])
    B2 = float(request.form["B2"])
    C2 = float(request.form["C2"])

    # =========================
    # CÁLCULO DE TEMPERATURAS
    # =========================
    step = (T_high - T_low) / n_div
    temperaturas = [T_low + i * step for i in range(n_div + 1)]

    # =========================
    # FUNCIÓN ANTOINE
    # =========================
    def antoine(A, B, C, T):
        return 10 ** (A - (B / (T + C)))

    # =========================
    # LISTAS
    # =========================
    X_a, Y_a, T_vals = [], [], []

    # =========================
    # CÁLCULO
    # =========================
    for i, T in enumerate(temperaturas):

        if i == 0:
            Pa = P_op
            Pb = antoine(A2, B2, C2, T)
            Xa = 1.0
            Ya = 1.0

        elif i == len(temperaturas) - 1:
            Pa = antoine(A1, B1, C1, T)
            Pb = P_op
            Xa = 0.0
            Ya = 0.0

        else:
            Pa = antoine(A1, B1, C1, T)
            Pb = antoine(A2, B2, C2, T)
            Xa = (P_op - Pb) / (Pa - Pb)
            Ya = (Xa * Pa) / P_op

        X_a.append(Xa)
        Y_a.append(Ya)
        T_vals.append(T)

    # =========================
    # GRÁFICAS (FORMATO A4)
    # =========================
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(8.27, 11.69),   # A4 vertical
        sharex=True
    )

    # =========================
    # DIAGRAMA T–x–y
    # =========================
    ax1.plot(X_a, T_vals, color='red',
             linewidth=1, label="Curva de burbuja")
    ax1.plot(Y_a, T_vals, color='blue',
             linewidth=1, label="Curva de rocío")

    ax1.set_ylabel("Temperatura (°C)")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(min(T_vals), max(T_vals))

    ax1.set_xticks([i / 10 for i in range(11)])
    ax1.set_xticks([i / 100 for i in range(101)], minor=True)

    ax1.set_yticks(range(int(min(T_vals)), int(max(T_vals)) + 5, 5))
    ax1.set_yticks(range(int(min(T_vals)), int(max(T_vals)) + 1, 1), minor=True)

    ax1.tick_params(which='major', length=6, direction='out')
    ax1.tick_params(which='minor', length=3, direction='out')

    ax1.grid(which='major', linewidth=0.6)
    ax1.grid(which='minor', linewidth=0.3)
    ax1.legend()

    # =========================
    # DIAGRAMA y–x
    # =========================
    ax2.plot(X_a, Y_a, color='green',
             linewidth=1, label="Curva de equilibrio")
    ax2.plot([0, 1], [0, 1], color='black',
             linewidth=1, label="Curva de operación")

    ax2.set_xlabel("Xa (fracción molar en líquido)")
    ax2.set_ylabel("Ya (fracción molar en vapor)")

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    ax2.set_xticks([i / 10 for i in range(11)])
    ax2.set_yticks([i / 10 for i in range(11)])

    ax2.set_xticks([i / 100 for i in range(101)], minor=True)
    ax2.set_yticks([i / 100 for i in range(101)], minor=True)

    ax2.tick_params(which='major', length=6, width=0.8, direction='out')
    ax2.tick_params(which='minor', length=3, width=0.5, direction='out')

    ax2.grid(which='major', linewidth=0.6)
    ax2.grid(which='minor', linewidth=0.3)
    ax2.legend()

    # =========================
    # SALIDA WEB
    # =========================
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    plt.close()
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")

# ======================================================
# DESTILACIÓN – PONCHON SAVARIT (WEB)
# ======================================================
@app.route("/destilacion_ponchon", methods=["GET", "POST"])
def destilacion_ponchon():

    if request.method == "GET":
        return render_template("destilacion_ponchon.html")

    # =========================
    # ENTRADA DE DATOS
    # =========================
    T_low = float(request.form["T_low"])
    T_high = float(request.form["T_high"])
    P_op = float(request.form["P_op"])
    n_div = int(request.form["n_div"])

    A1 = float(request.form["A1"])
    B1 = float(request.form["B1"])
    C1 = float(request.form["C1"])

    A2 = float(request.form["A2"])
    B2 = float(request.form["B2"])
    C2 = float(request.form["C2"])

    cp_liq_A = float(request.form["cp_liq_A"])
    cp_liq_B = float(request.form["cp_liq_B"])
    cp_vap_A = float(request.form["cp_vap_A"])
    cp_vap_B = float(request.form["cp_vap_B"])
    lambdaA = float(request.form["lambdaA"])
    lambda_ab = float(request.form["lambda_ab"])
    T0 = float(request.form["T0"])

    # =========================
    # CÁLCULO DE TEMPERATURAS
    # =========================
    step = (T_high - T_low) / n_div
    temperaturas = [T_low + i * step for i in range(n_div + 1)]

    def antoine(A, B, C, T):
        return 10 ** (A - (B / (T + C)))

    X_a, Y_a, T_vals = [], [], []
    h_vals, H_vals = [], []

    TrefL = T_low

    lambdaB = cp_vap_B * (T_high - T0) + lambda_ab - cp_vap_A * (T_high - T0)

    for i, T in enumerate(temperaturas):

        if i == 0:
            Pa = P_op
            Pb = antoine(A2, B2, C2, T)
            Xa, Ya = 1.0, 1.0

        elif i == len(temperaturas) - 1:
            Pa = antoine(A1, B1, C1, T)
            Pb = P_op
            Xa, Ya = 0.0, 0.0

        else:
            Pa = antoine(A1, B1, C1, T)
            Pb = antoine(A2, B2, C2, T)
            Xa = (P_op - Pb) / (Pa - Pb)
            Ya = (Xa * Pa) / P_op

        X_a.append(Xa)
        Y_a.append(Ya)
        T_vals.append(T)

        h = Xa * cp_liq_A * (T - TrefL) + (1 - Xa) * cp_liq_B * (T - TrefL)
        h_vals.append(h)

        H = Ya * (lambdaA + cp_vap_A * (T - T0)) + (1 - Ya) * (lambdaB + cp_vap_B * (T - T0))
        H_vals.append(H)

    # =========================
    # GRÁFICAS – FORMATO A4
    # =========================
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(8.27, 11.69),   # A4 vertical
        sharex=False
    )

    # =========================
    # DIAGRAMA H–X
    # =========================
    ax1.plot(X_a, h_vals, color='blue',
             linewidth=1.2, label="Líquido")
    ax1.plot(Y_a, H_vals, color='red',
             linewidth=1.2, label="Vapor")

    ax1.set_xlabel("Fracción molar")
    ax1.set_ylabel("Entalpía (kJ/kmol)")
    ax1.set_xlim(0, 1)

    ax1.set_xticks([i / 10 for i in range(11)])
    ax1.set_xticks([i / 100 for i in range(101)], minor=True)

    ax1.tick_params(which='major', length=6, direction='out')
    ax1.tick_params(which='minor', length=3, direction='out')

    ax1.grid(which='major', linewidth=0.6)
    ax1.grid(which='minor', linewidth=0.3)

    ax1.legend()

    # =========================
    # DIAGRAMA Y–X
    # =========================
    ax2.plot(X_a, Y_a, color='green',
             linewidth=1.2, label="Curva de equilibrio")
    ax2.plot([0, 1], [0, 1], color='black',
             linewidth=1.2, label="Curva de Operación")

    ax2.set_xlabel("Xa (fracción molar en líquido)")
    ax2.set_ylabel("Ya (fracción molar en vapor)")

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    ax2.set_xticks([i / 10 for i in range(11)])
    ax2.set_yticks([i / 10 for i in range(11)])

    ax2.set_xticks([i / 100 for i in range(101)], minor=True)
    ax2.set_yticks([i / 100 for i in range(101)], minor=True)

    ax2.tick_params(which='major', length=6, direction='out')
    ax2.tick_params(which='minor', length=3, direction='out')

    ax2.grid(which='major', linewidth=0.6)
    ax2.grid(which='minor', linewidth=0.3)

    ax2.legend()

    # =========================
    # SALIDA WEB
    # =========================
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    plt.close()
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")


# ======================================================
# ABSORCIÓN GAS–LÍQUIDO (WEB)
# ======================================================
@app.route("/absorcion", methods=["GET", "POST"])
def absorcion():

    if request.method == "GET":
        return render_template("absorcion.html")

    # ===== Entrada de datos =====
    Pvap = float(request.form["Pvap"])
    Pope = float(request.form["Pope"])
    y_inicial = float(request.form["y_inicial"])

    orientacion = request.form["orientacion"].lower()

    # ===== Conversión a relación molar =====
    Y_inicial = y_inicial / (1 - y_inicial)

    # ===== Pendiente =====
    m = Pvap / Pope

    # ===== Extensión moderada del comportamiento =====
    y_limite = y_inicial * 1.2

    X_rel = []
    Y_rel = []

    paso = 0.0001
    x = 0.0

    while True:
        y = m * x
        if y >= y_limite:
            break

        X = x / (1 - x)
        Y = y / (1 - y)

        X_rel.append(X)
        Y_rel.append(Y)

        x += paso

    # ===== CONFIGURACIÓN DE FIGURA SEGÚN ORIENTACIÓN =====
    if orientacion == "h":
        fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 horizontal
    else:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 vertical

    # ===== GRÁFICA =====
    ax.plot(
        X_rel, Y_rel,
        color='red',
        linewidth=0.8,
        label="Curva de equilibrio"
    )

    # Marca de la concentración inicial
    ax.plot(
        [-0.0005], [Y_inicial],
        marker="_",
        markersize=15,
        color='black',
        label="Y inicial"
    )

    # Límites
    ax.set_xlim(0, max(X_rel))
    ax.set_ylim(0, max(Y_rel))

    # Etiquetas
    ax.set_xlabel("X (Relación molar en líquido)")
    ax.set_ylabel("Y (Relación molar en gas)")

    # Rejilla simple
    ax.grid(True, linewidth=0.6)

    # Leyenda
    ax.legend()

    plt.tight_layout()

    # ===== SALIDA WEB (SIN ARCHIVOS) =====
    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    plt.close()
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")

# ======================================================
# EXTRACCIÓN SÓLIDO–LÍQUIDO (WEB)
# ======================================================
@app.route("/extraccion-sl", methods=["GET", "POST"])
def extraccion_sl():

    if request.method == "GET":
        return render_template("extraccion_sl.html")

    # ===== 1. Número de pares de datos =====
    n = int(request.form["n"])

    # ===== 2. Ingreso de datos =====
    A_vals = []
    B_vals = []

    for i in range(n):
        A_vals.append(float(request.form[f"A{i}"]))
        B_vals.append(float(request.form[f"B{i}"]))

    # ===== 3. DataFrame =====
    data = pd.DataFrame({
        "A": A_vals,
        "B": B_vals
    })

    # ===== 4. Cálculos (IGUALES) =====
    data["A%"] = 1 / (1 + data["B"])
    data["B%"] = (data["B"] * (1 - data["A"])) / (1 + data["B"])
    data["C%"] = (data["A"] * data["B"]) / (1 + data["B"])

    # ===== 5. GRÁFICA (A4 HORIZONTAL) =====
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 horizontal

    # Curva experimental
    ax.plot(data["B%"], data["C%"], color="red", linewidth=1.1)

    # Línea diagonal de referencia
    ax.plot([0, 1], [1, 0], color="black", linewidth=1.2)

    # Límites
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ===== Ticks =====
    major_ticks = np.arange(0, 1.1, 0.1)
    minor_ticks = np.arange(0, 1.01, 0.01)

    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(minor_ticks, minor=True)

    # Marcas exteriores
    ax.tick_params(axis='both', which='major', length=7, width=1.2, direction='out')
    ax.tick_params(axis='both', which='minor', length=3, width=0.8, direction='out')

    # Rejilla
    ax.grid(which='major', linestyle='--', linewidth=0.6, alpha=0.6)
    ax.grid(which='minor', linestyle=':', linewidth=0.3, alpha=0.4)

    # Etiquetas
    ax.set_xlabel("Fracción en peso del solvente (B%)")
    ax.set_ylabel("Fracción en peso del soluto (C%)")
    ax.set_title("Extracción sólido–líquido")

    # Ajuste final
    plt.tight_layout()

    # ===== SALIDA WEB (SIN GUARDAR ARCHIVO) =====
    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    plt.close()
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")


# ======================================================
# EXTRACCIÓN LÍQUIDO–LÍQUIDO (WEB)
# ======================================================
@app.route("/extraccion-ll", methods=["GET", "POST"])
def extraccion_ll():

    if request.method == "GET":
        return render_template("extraccion-ll.html")

    import math

    # ===== 1. Número de puntos =====
    n = request.form.get("n")
    if n is None:
        return "Falta el número de puntos (n)", 400
    n = int(n)

    B_a, C_a = [], []
    B_o, C_o = [], []

    # ===== 2. FASE ACUOSA =====
    for i in range(n):
        try:
            A = float(request.form.get(f"Aa{i}"))
            B = float(request.form.get(f"Ba{i}"))
            C = float(request.form.get(f"Ca{i}"))
        except (TypeError, ValueError):
            return f"Faltan datos en fase acuosa, fila {i}", 400

        if abs(A + B + C - 100) > 0.01:
            return f"A + B + C debe ser 100 % (fase acuosa, fila {i})", 400

        B_a.append(B)
        C_a.append(C)

    # ===== 3. FASE ORGÁNICA =====
    for i in range(n):
        try:
            A = float(request.form.get(f"Ao{i}"))
            B = float(request.form.get(f"Bo{i}"))
            C = float(request.form.get(f"Co{i}"))
        except (TypeError, ValueError):
            return f"Faltan datos en fase orgánica, fila {i}", 400

        if abs(A + B + C - 100) > 0.01:
            return f"A + B + C debe ser 100 % (fase orgánica, fila {i})", 400

        B_o.append(B)
        C_o.append(C)

    # ===== 4. Conversión =====
    XB_a = [b / 100 for b in B_a]
    XC_a = [c / 100 for c in C_a]

    XB_o = [b / 100 for b in B_o]
    XC_o = [c / 100 for c in C_o]

    X_dist_a = [1 + x for x in XC_a]
    X_dist_o = XC_o

    # ===== 5. Límites =====
    x_max_real = max(X_dist_a)
    y_max_real = max(max(XC_a), max(XC_o))

    x_lim = math.ceil(x_max_real * 10) / 10
    y_lim = math.ceil(y_max_real * 10) / 10

    # ===== 6. GRÁFICA =====
    plt.figure(figsize=(11.69, 8.27), dpi=100)

    # Triángulo
    plt.plot([0, 1], [0, 0], 'k-')
    plt.plot([0, 0], [0, 1], 'k-')
    plt.plot([1, 0], [0, 1], 'k-')

    # Curvas
    plt.plot(XB_a, XC_a, 'r-o', markersize=3)
    plt.plot(XB_o, XC_o, 'r-o', markersize=3)
    plt.plot(X_dist_a, X_dist_o, 'r-o', markersize=3)

    # Línea de operación 45°
    x_op = [1 + i * (x_lim - 1) / 100 for i in range(101)]
    y_op = [i * (x_lim - 1) / 100 for i in range(101)]
    plt.plot(x_op, y_op, 'k-')

    plt.xlim(0, x_lim)
    plt.ylim(0, y_lim)

    plt.xlabel('XB   →   XC acuosa + 1')
    plt.ylabel('XC')
    plt.title('Extracción líquido–líquido')

    # Cuadrícula
    plt.xticks([i * 0.1 for i in range(int(x_lim * 10) + 1)])
    plt.yticks([i * 0.1 for i in range(int(y_lim * 10) + 1)])
    plt.gca().set_xticks([i * 0.01 for i in range(int(x_lim * 100) + 1)], minor=True)
    plt.gca().set_yticks([i * 0.01 for i in range(int(y_lim * 100) + 1)], minor=True)

    plt.grid(True, which='major')
    plt.grid(True, which='minor', linewidth=0.3)

    plt.tight_layout()

    # ===== 7. SALIDA WEB =====
    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    plt.close()
    img.seek(0)

    return Response(img.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)