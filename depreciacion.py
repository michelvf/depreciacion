from collections import OrderedDict
import os
import platform
import datetime as dt
import calendar


""" Para calcular la depreciación según varios métodos """

def PedirCosto() -> float:
    """Pedir el costo y validar"""
    
    costo = float(input("¿Cuánto costó comprar el Activo?: "))
    if costo <= 0:
        raise ValueError("El costo no puede ser negativo, ni igual a cero.")
    
    return costo


def PedirValorSalvamento(costo: float) -> float:
    """Pedir y validar el valor de salvamento"""
    
    valor_salvamento = float(input('¿Hasta qué valor lo va utilizar?: '))
    if valor_salvamento < 0:
        raise ValueError("Este valor no puede ser negativo.")
    if valor_salvamento >= costo:
            raise ValueError("E valor de salvamento no puede ser igual o mayor al costo.")
    
    return valor_salvamento


def sumar_meses(fecha: dt.date, meses: int) -> dt.date:
    """Suma 'meses' a una fecha, ajustando el día si el mes destino es más corto."""
    total = fecha.month - 1 + meses
    año = fecha.year + total // 12
    mes = total % 12 + 1
    dia = min(fecha.day, calendar.monthrange(año, mes)[1])
    return dt.date(año, mes, dia)


def desglosar_por_año_calendario(fecha_inicio: dt.date, duracion_meses: int, venta=False) -> dict:
    """
    Divide 'duracion_meses' en meses, asignando cada mes al año calendario
    en el que comienza. Cada año calendario termina el 31 de diciembre.

    Retorna:
        años            -> años completos (duracion_meses // 12)
        meses_restantes -> meses sobrantes (duracion_meses % 12)
        arreglo         -> meses por año calendario, ej: [8, 12, 10]
        años_calendario -> lista de años, ej: [2020, 2021, 2022]
        periodos        -> dict {año: meses}
        detalle_meses   -> lista con desde/hasta de cada mes
        fecha_fin       -> fecha_inicio + duracion_meses
    """
    
    if duracion_meses < 0:
        raise ValueError("La duración no puede ser negativa.")

    periodos = OrderedDict()   # año -> meses
    detalle = []

    if venta:
        duracion_meses = int((venta - fecha_inicio).days/30)
    
    for k in range(duracion_meses):
        inicio_mes = sumar_meses(fecha_inicio, k)
        fin_mes    = sumar_meses(fecha_inicio, k + 1)
        anno        = inicio_mes.year

        periodos[anno] = periodos.get(anno, 0) + 1
        detalle.append({
            "num": k + 1,
            "anno": anno,
            "desde": inicio_mes,
            "hasta": fin_mes,
        })

    return {
        "annos": duracion_meses // 12,
        "meses_restantes": duracion_meses % 12,
        "arreglo": list(periodos.values()),
        "años_calendario": list(periodos.keys()),
        "periodos": dict(periodos),
        "detalle_meses": detalle,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": sumar_meses(fecha_inicio, duracion_meses),
    }


def pedir_fecha(mensaje: str = "Introduce una fecha (dd/mm/YYYY): ") -> dt.date:
    """Pedir la fecha, validarla y devolverla en formato date"""
    
    while True:
        entrada = input(mensaje).strip()
        try:
            fecha = dt.datetime.strptime(entrada, "%d/%m/%Y").date()
            # Opcional: rechazar fechas futuras
            if fecha > dt.date.today():
                print("La fecha no puede ser futura. Inténtalo de nuevo.")
                continue
            return fecha
        except ValueError:
            print("Formato incorrecto o fecha inválida. Usa dd/mm/YYYY (ej: 15/05/1990).")


def FormatoMoneda(valor: float, simbolo: str = "$") -> str:
    """Dar formato moneda a un número dado"""
    
    return f"{simbolo}{valor:,.2f}"


def desglose_syd(costo: float, valor_residual: float, tiempo: int) -> dict:
    if costo < valor_residual:
        raise ValueError("El costo no puede ser menor que el valor residual.")

    # Arreglo descendente: [4, 3, 2, 1]
    digitos = list(range(tiempo, 0, -1))

    sumatoria = sum(digitos)            # 4+3+2+1 = 10
    base      = costo - valor_residual  # 10000 - 1000 = 9000
    factor    = base / sumatoria        # 900.0

    # Cuota de depreciación por año: factor × cada elemento del arreglo
    cuotas = [factor * d for d in digitos]

    return {
        "digitos": digitos,         # [4, 3, 2, 1]
        "sumatoria": sumatoria,     # 10
        "base": base,               # 9000
        "factor": factor,           # 900.0
        "cuotas": cuotas,           # [3600.0, 2700.0, 1800.0, 900.0]
    }


def AsientCompra(activo: str, valor: float, pago="Efectos por Pagar") -> str:
    """Asiento de la adquisición del Activo"""

    print("\nAsiento de Adquisición:")
    print("\n\t\t\t\tDebe\t\tHaber")
    print(f"{activo}\t\t\t{FormatoMoneda(valor)}")
    print(f"\t{pago}\t\t\t{FormatoMoneda(valor)}\n")


def DepTiempo(dep, year:int) ->str:
    """Mostrar la depreciasión en el tiempo"""
    print("\nAño\tDepreciación")
    for i in range(len(dep)):
        print(f"{year}\t{FormatoMoneda(dep[i])}")
        year = int(year) + 1


def PedirDatos() -> tuple[float, float, int, dt.date]:
    """Solicitud de datos y validación"""
    
    costo = PedirCosto()
    valor_salvamento = PedirValorSalvamento(costo)
    vida_util_probable = int(input("¿Cuántos años cree que le va a durar el activo?: "))
    if vida_util_probable <= 0:
        raise ValueError("El tiempo de los años debe ser un entero positivo y mayor que cero.")
    fecha_compra = pedir_fecha()
        
    return costo, valor_salvamento, vida_util_probable, fecha_compra


def LineaRecta():
    """Método Línea Recta"""
    
    limpiar_pantalla()
    print("=== Cálculo de la depreciación por el Método de Línea Recta ===")
    print(f"\nAyuda:\n\t- Cuando se dice 'activo' se refire a la máquina, el equipo, el medio, el objeto que compró.")
    print(f"\t- Cuando se pregunta hasta qué valor lo va a utilizar, se refiere al valor estimado")
    print(f"\t  que tendrá el activo cuando se termine de depreciar.\n")
    
    costo, valor_salvamento, vida_util_probable, fecha_compra = PedirDatos()
    
    vida_util_probable_meses = vida_util_probable * 12
    depreciacion = (costo - valor_salvamento) / vida_util_probable
    
    r = desglosar_por_año_calendario(fecha_compra, vida_util_probable_meses)
    
    AsientCompra("Moviliario", costo)
    
    print(f"\nDepreciación: {FormatoMoneda(depreciacion)} anual, o {FormatoMoneda(depreciacion/12)} mensual")
    
    dep_acumulada = 0
    print("\nDetalle por año calendario:")
    print("Años\tMeses\tDepreciación\tDepreciación Acumulada")
    for año, meses in r["periodos"].items():
        dep_mensual = meses * depreciacion/12
        dep_acumulada += dep_mensual
        print(f"{año}\t{meses}\t{FormatoMoneda(dep_mensual)}\t{FormatoMoneda(dep_acumulada)}" )
    
    input("\nPresiona Enter para volver al menú...")


def DigitosDecrecientes():
    """Método de los Dígitos Decrecientes"""
    
    limpiar_pantalla()
    
    print("=== Cálculo de la Depreciación por el Método de los Dígitos Decrecientes ===\n")
    print(f"Este método se basa en principalmente a depreciar cantidades mayores los primero años de existencia del Activo y cantidades menores en los ultimos años (en forma decreciente)\n")
    print("Este razonamiento es en virtud de que el Activo nececita gastar menos en reparacinoes y manteminientos en los primero años, lo que se compensa con los mayor Depreciación, y los últimos años, como es lógico, necesita gastar más en mantenimiento y reparaciones, lo que se compensa con una menor Depreciación.\n")
    
    costo, valor_residual, vida_util_probable, fecha_compra = PedirDatos()
    
    # Arreglo descendente: [4, 3, 2, 1]
    digitos = list(range(vida_util_probable, 0, -1))

    sumatoria = sum(digitos)            # 4+3+2+1 = 10
    base      = costo - valor_residual  # 10000 - 1000 = 9000
    factor    = base / sumatoria        # 900.0
    
    AsientCompra("Vehículo", costo)
    
    # Las fechas
    print(f"La fecha de compra es: {fecha_compra} y la vida útil: {vida_util_probable}\n")
    r = desglosar_por_año_calendario(fecha_compra, vida_util_probable*12)
    cuotas = [factor * d for d in digitos]
    
    print(f"Arreglo son: {len(r['arreglo'])}\n")
    
    pagos = []
    for i in range(len(r['arreglo'])):
        if i == 0:
            pagos.append(cuotas[i] * r['arreglo'][0] / 12)
            #print(f"i = {i} y pagos agregó: {pagos[i]}, cuotas: {cuotas[i]} * {r['arreglo'][0]} / 12")
        else:            
            a = cuotas[i-1] * r['arreglo'][0] / 12
            
            if i < len(cuotas):
                h = cuotas[i] * r['arreglo'][0] / 12
                # print(f"cuotas: {cuotas[i]} * {r['arreglo'][0]} / 12")
            else:
                h = 0
            
            pagos.append(a + h)
            # print(f"i = {i} y agregó: {pagos[i]}")
    
    # print(f"Terminó el cálculo, pagos tiene {len(pagos)} registro\n")
    
    
    # Cuota de depreciación por año: factor × cada elemento del arreglo

    print("Tabla de Depreciación:")
    print("Año\tDígito\t\t\tDepreciación\tValor libro\tPor fechas")
    
    dep_acum = 0
    for i in range(len(digitos)):
        dep_acum += cuotas[i]
        print(f"{i+fecha_compra.year}\t{FormatoMoneda(factor)} x {digitos[i]}\t\t{FormatoMoneda(cuotas[i])}\t{FormatoMoneda(costo-dep_acum)}\t{FormatoMoneda(pagos[i])}")
    
    
    input("\nPresiona Enter para volver al menú...")
    

def HorasMaquinas():
    """Método de Horas Máquinas"""
    
    limpiar_pantalla()
    print("=== Cálculo de la Depreciación por el Método de Horas Máquinas ===\n")
    print("\nEste Método sirve exclusivamente para depreciar ciertos medios de producción, como es el caso de una máquina en una empresa de caracer industrial.\n")
    print("En este caso se estima el número total de horas que puede trabajar una máquina en su vida útil.\n")
    
    costo = PedirCosto()
    valor_salvamento = PedirValorSalvamento(costo)
    horas_maq = float(input('¿Cuántas horas estima que trabaje la Activo?: '))
    if valor_salvamento <= 0:
        raise ValueError("Este valor no puede ser negativo, ni igual a cero.")
    
    factor_depreciacion = (costo - valor_salvamento) / horas_maq
    
    AsientCompra("Maquinaria", costo, "Efectivo en Banco")
    
    print(f"\nEl equipo debe depreciar: {FormatoMoneda(factor_depreciacion)} por cada hora utilizada.\n")
    
    print(f"Si en el año el equipo trabajó 5 mil horas, debe depreciar: 5000 horas x {FormatoMoneda(factor_depreciacion)} = {FormatoMoneda(factor_depreciacion*5000)}\n")
    
    input("\nPresiona Enter para volver al menú...")


def UnidadesDeProduccion():
    """Método de Unidades de Producción"""
    
    limpiar_pantalla()
    print("=== Cálculo de la Depreciación por el Método de Unidades de Producción ===\n")
    
    print("\nEste Método sirve exclusivamente para depreciar ciertos medios de producción, como es el caso de una máquina en una empresa de caracer industrial.\n")
    print("En este caso se estima el número total de unidades que puede producir la máquina en su vida útil.\n")
        
    costo = PedirCosto()
    valor_salvamento = PedirValorSalvamento(costo)
    unidades_produccion = int(input("Cuántas unidades va a producir el Activo en toda su vida útil? "))
    if unidades_produccion <= 0:
        raise ValueError("Las unidades de produción son mayores que 0")
    
    factor_depreciacion = (costo -  valor_salvamento) / unidades_produccion
    
    AsientCompra("Maquinaria", costo)
    
    print(f"\nEl Factor de Depreciación del Activo es de {FormatoMoneda(factor_depreciacion)} por unidad producida.\n")
    
    print(f"Si en el año produjeron 27 mil unidades, la Depreciación anual es de {FormatoMoneda(factor_depreciacion * 27000)}")
    
    input("\nPresiona Enter para volver al menú...")


def PorcentajeFijoSobreSaldoVariable():
    """Método de porcentaje fijo sobre Saldo Variable"""
    
    limpiar_pantalla()
    print("=== Cálculo de la Depreciación por el Método de porcenaje fijo sobre Saldo Variable ===\n")
    print("Por este método la Depreciación anual se determina en base a un porcentaje fijo, el cuál se le aplica al Valor del Activo según libros\n")
    print("Este Método es de poca utilidad, porque el Activo nunca se termina de depreciar, porque siempre queda un saldo que depreciar.\n")
    
    costo = PedirCosto()
    porcentaje = float(input("Porcentaje fijo a depreciar: "))
    if porcentaje <= 0:
        raise ValueError("El porcentaje debe ser un entero positivo y mayor que cero.")
    fecha = pedir_fecha()
    
    # print(f"\nLa Depreciación del 1er año es del {porcentaje}% para un valor de: {depre}\n")
    
    AsientCompra("Moviliario", costo)
    
    depre_acu = 0
    print("\nAño\tValor del activo\tA depreciar\tDepreciación acumulada")
    for i in range(fecha.year, fecha.year+10):
        depre = costo * (porcentaje / 100)
        depre_acu += depre
        print(f"{i}\t{FormatoMoneda(costo)}\t\t{FormatoMoneda(depre)}\t{FormatoMoneda(depre_acu)}")
        costo = costo - depre
    input("\nPresiona Enter para volver al menú...")


def DesincorporacionDeActivo():
    """Método de Baja de un Activo"""
    
    limpiar_pantalla()
    print("=== Cálculo de la Depreciación cuando se le da baja un Activo ===\n")
    print("Este Método se usa cuando un Activo se le va a dar Baja.")
    print("Se puede dar baja o por Venta, Permuta, o Retiro del Activo.")
    
    costo = PedirCosto()
    valor_salvamento = PedirValorSalvamento(costo)
    duracion = int(input("Cuántos años va a durar el Activo: "))
    if not duracion.is_integer():
        raise ValueError("Debe ingresar un número entero")
    if duracion <= 0:
        raise ValueError("La duración del Activo no puede ser negativo, ni igual a cero.")
    fecha_compra = pedir_fecha("Fecha de la compra del activo: ")
    venta = input("¿Se vendió el producto? (s/n) ")
    if venta.lower() == 's':
        fecha_venta = pedir_fecha("Fecha de la venta del activo: ")
        precio_venta = float(input("¿A cuánto se vendió el Activo? "))
    
    
    tasa_depreciacion = (costo - valor_salvamento) / duracion
    
    AsientCompra("Vehículo", costo)
    
    if venta.lower() == 's':
        r = desglosar_por_año_calendario(fecha_compra, duracion * 12, fecha_venta)
    else:
        r = desglosar_por_año_calendario(fecha_compra, duracion * 12)
    
    dep =  OrderedDict()
    dep_acum = 0
    for i in range(len(r['arreglo'])):
        deprec = r["arreglo"][i] * tasa_depreciacion / 12
        dep[r['años_calendario'][i]] = deprec
        dep_acum += deprec
        
    segun_libros = costo - dep_acum
    print("\nValor Según Libros")
    print(f"Vehículo\t\t\t{FormatoMoneda(costo)}")
    print(f"menos: Depreciación Acumulada\t{FormatoMoneda(dep_acum)}\n")
    print(f"Valor según libros\t\t{FormatoMoneda(segun_libros)}")
    if venta.lower() == 's':
        print(f"Precio de Venta\t\t\t{FormatoMoneda(precio_venta)}")
        g_p = precio_venta - segun_libros
        if g_p > 0:
            G_P = "Ganancia en Venta"
        elif g_p < 0:
            G_P = "Pérdida en Venta"
        else:
            G_P = "Ganancia o Pérdida en Venta"
        print(f"{G_P}\t\t{FormatoMoneda(g_p)}")
    
    
    input("\nPresiona Enter para volver al menú...")


def Ayuda():
    """Ayuda de los métodos"""
    
    limpiar_pantalla()
    print("=== Zona de Ayuda de los Métodos de Depreciación ===\n")
        
        
    input("\nPresiona Enter para volver al menú...")


def limpiar_pantalla():
    """Limpia la consola en Windows, macOS o Linux."""
    sistema = platform.system()
    if sistema == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def main():
    opciones = {
        "1": LineaRecta,
        "2": DigitosDecrecientes,
        "3": HorasMaquinas,
        "4": UnidadesDeProduccion,
        "5": PorcentajeFijoSobreSaldoVariable,
        "6": DesincorporacionDeActivo,
        "7": Ayuda,
    }

    while True:
        limpiar_pantalla()
        print("=" * 40)
        print("           MENÚ PRINCIPAL")
        print("Para la calcular la depresiación según varios métodos:")
        print("=" * 40)
        print("1. Línea Recta.")
        print("2. Digitos Decrecientes.")
        print("3. Horas Máquinas.")
        print("4. Unidad de Producción.")
        print("5. Porcentaje fijo sobre saldo Variable.")
        print("6. Desincorporación del activo.")
        print("7. Ayuda.")
        print("T. Terminar")
        print("=" * 40)

        opcion = input("Escoge una opción (1-7 o T): ").strip()

        if opcion.upper() == "T":
            limpiar_pantalla()
            print("¡Hasta luego! Programa finalizado.")
            break
        elif opcion.upper == "Q":
            limpiar_pantalla()
            print("¡Hasta luego! Programa finalizado.")
            break
        elif opcion in opciones:
            opciones[opcion]()
        else:
            print("\nOpción no válida. Intenta de nuevo.")
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    main()