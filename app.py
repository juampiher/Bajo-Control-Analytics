import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# LOGIN SIMPLE
# =========================
usuarios = {
    "cliente1": {"password": "1234", "activo": True},
    "cliente2": {"password": "abcd", "activo": False}
}

# =========================
# TITULO PRINCIPAL Y DESCRIPCION
# =========================
st.title("HOLAAAAAAAAAAAA")
st.markdown(
    "<h1 style='text-align: center;'>📊 Bajo Control Analytics</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Analizá tu negocio de forma simple y tomá mejores decisiones</p>",
    unsafe_allow_html=True
)

# =========================
# FORMULARIO DE LOGIN
# =========================
if "login" not in st.session_state or not st.session_state["login"]:

    st.subheader("Iniciar sesión")

    usuario_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        if usuario_input in usuarios:
            if usuarios[usuario_input]["password"] == password_input:

                if usuarios[usuario_input]["activo"]:
                    st.session_state["login"] = True
                    st.session_state["usuario"] = usuario_input
                    st.rerun()
                else:
                    st.error("Usuario inactivo. Contactate para reactivar acceso.")
            else:
                st.error("Usuario o contraseña incorrecta")
        else:
            st.error("Usuario o contraseña incorrecta")

    st.stop()

# =========================
# SI NO ESTÁ LOGUEADO, NO MUESTRA LA APP
# =========================
if "login" not in st.session_state or not st.session_state["login"]:
    st.stop()

# =========================
# SEPARADOR
# =========================
st.write("--------------------------------------------------------------")

# =========================
# BIENVENIDA AL USUARIO
# =========================
st.markdown(
    f"<h3 style='text-align: center;'>👋 Bienvenido, {st.session_state['usuario']}</h3>",
    unsafe_allow_html=True
)

# =========================
# BOTON CERRAR SESION
# =========================
col_logout1, col_logout2 = st.columns([6,2])

with col_logout2:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

st.write("Subí tu archivo Excel o CSV")

# =========================
# PLANTILLA DESCARGABLE
# =========================
st.info("💡 Podés descargar una plantilla modelo para completar fácilmente.")

plantilla_df = pd.DataFrame({
    "fecha": ["01/01/2026"],
    "producto": ["amoladora"],
    "costo_unitario": [50000],
    "precio_unitario": [80000],
    "cantidad": [2]
})

csv_plantilla = plantilla_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar plantilla modelo",
    data=csv_plantilla,
    file_name="plantilla_bajo_control_analytics.csv",
    mime="text/csv"
)

# =========================
# FORMATO ESPERADO DEL ARCHIVO
# =========================
st.caption("Formato esperado del archivo")

st.dataframe(plantilla_df, hide_index=True)

# =========================
# SUBIR ARCHIVO
# =========================
archivo = st.file_uploader("Seleccionar archivo", type=["csv", "xlsx"])

if archivo is not None:

    # =========================
    # LEER ARCHIVO
    # =========================
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)

    # =========================
    # VALIDAR COLUMNAS OBLIGATORIAS
    # =========================
    columnas_obligatorias = ["fecha", "producto", "costo_unitario", "precio_unitario", "cantidad"]

    if not all(columna in df.columns for columna in columnas_obligatorias):
        st.error("❌ El archivo no tiene el formato correcto.")
        st.write("Columnas obligatorias:", columnas_obligatorias)

    else:
        # =========================
        # PREPARACION DE DATOS
        # =========================
        df["fecha"] = pd.to_datetime(df["fecha"])

        df["venta_total"] = df["precio_unitario"] * df["cantidad"]
        df["costo_total"] = df["costo_unitario"] * df["cantidad"]
        df["ganancia"] = df["venta_total"] - df["costo_total"]

        # =========================
        # FILTROS
        # =========================
        st.subheader("Filtros")

        opciones_producto = ["Todos"] + list(df["producto"].unique())

        producto_seleccionado = st.selectbox(
            "Seleccionar producto",
            opciones_producto
        )

        fecha_min = df["fecha"].min().date()
        fecha_max = df["fecha"].max().date()

        col_fecha1, col_fecha2 = st.columns(2)

        with col_fecha1:
            fecha_inicio = st.date_input("Fecha desde", fecha_min)

        with col_fecha2:
            fecha_fin = st.date_input("Fecha hasta", fecha_max)

        st.write(
            f"📅 Período analizado: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
        )

        # =========================
        # FILTRADO DE DATOS
        # =========================
        if producto_seleccionado == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df["producto"] == producto_seleccionado]

        df_filtrado = df_filtrado[
            (df_filtrado["fecha"] >= pd.to_datetime(fecha_inicio)) &
            (df_filtrado["fecha"] <= pd.to_datetime(fecha_fin))
        ]

        # =========================
        # VALIDAR SI HAY DATOS LUEGO DE FILTRAR
        # =========================
        if df_filtrado.empty:
            st.warning("No hay datos para los filtros seleccionados.")

        else:
            st.write("Vista previa de los datos:")
            st.dataframe(df_filtrado)

            # =========================
            # METRICAS
            # =========================
            st.subheader("Métricas del negocio")

            ventas_totales = df_filtrado["venta_total"].sum()
            ganancia_total = df_filtrado["ganancia"].sum()
            unidades = df_filtrado["cantidad"].sum()
            costo_total = df_filtrado["costo_total"].sum()

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Ventas totales", ventas_totales)
            col2.metric("Costo total", costo_total)
            col3.metric("Ganancia total", ganancia_total)
            col4.metric("Unidades", unidades)

            # =========================
            # GRAFICO
            # =========================
            st.subheader("Ventas por producto")

            ventas_por_producto = df_filtrado.groupby("producto")["venta_total"].sum().reset_index()

            fig = px.bar(
                ventas_por_producto,
                x="producto",
                y="venta_total",
                title="Ventas totales por producto"
            )

            st.plotly_chart(fig)

            # =========================
            # INSIGHTS
            # =========================
            st.subheader("Insights")

            producto_top = df_filtrado.groupby("producto")["venta_total"].sum().idxmax()
            producto_mas_ganancia = df_filtrado.groupby("producto")["ganancia"].sum().idxmax()
            producto_peor = df_filtrado.groupby("producto")["ganancia"].sum().idxmin()
            producto_mas_unidades = df_filtrado.groupby("producto")["cantidad"].sum().idxmax()

            margen = (ganancia_total / ventas_totales) * 100

            st.write("Producto más vendido:", producto_top)
            st.write("Producto más rentable:", producto_mas_ganancia)
            st.write("Producto menos rentable:", producto_peor)
            st.write(f"Margen promedio: {margen:.2f}%")
            st.write("Producto más vendido (unidades):", producto_mas_unidades)

            if margen < 20:
                st.error("⚠️ Margen bajo. Revisar precios o costos.")

            # =========================
            # PRODUCTOS CON PERDIDA
            # =========================
            productos_perdida = df_filtrado.groupby("producto")["ganancia"].sum()
            productos_perdida = productos_perdida[productos_perdida < 0]

            if not productos_perdida.empty:
                st.error("🚨 Productos con pérdida:")
                for producto, ganancia in productos_perdida.items():
                    st.write(f"{producto}: {ganancia}")

            # =========================
            # RECOMENDACIONES
            # =========================
            st.subheader("Recomendaciones")

            if margen < 10:
                st.error("🔴 Margen muy bajo o negativo. Revisá precios y costos.")
            elif margen < 25:
                st.warning("🟡 Margen medio. Podrías mejorar la rentabilidad.")
            else:
                st.success("🟢 Buen margen general.")

            if not productos_perdida.empty:
                st.warning("Revisá productos con pérdida: subir precios o bajar costos.")

            ventas_resumen = df_filtrado.groupby("producto")["venta_total"].sum()
            porcentaje_top = (ventas_resumen.max() / ventas_resumen.sum()) * 100

            if porcentaje_top > 50:
                producto_top_ventas = ventas_resumen.idxmax()
                st.warning(
                    f"⚠️ Alta dependencia de un producto: {producto_top_ventas} representa el {porcentaje_top:.2f}% de las ventas."
                )