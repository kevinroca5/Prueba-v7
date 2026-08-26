# Análisis de Partidos — LaLiga (multipágina)

Plataforma de prueba dividida en "slides" (páginas), como en Power BI, para analizar el
histórico de partidos de varios equipos.

## Páginas

- **🔴 Análisis Rival** — informe general (encabeza con % Posesión y estilo, no con
  goles), fortalezas y debilidades automáticas frente a la media real de LaLiga 24/25
  (con percentil y ranking, no z-scores en crudo), y filtro completo por categoría de
  métrica: **General, Ofensivas, Defensivas, Posesión y Estilo** — con sliders de rango
  para cada una.
- **🔵 Análisis Propio** — gráficos de evolución partido a partido (con media móvil de 5
  partidos y tira de resultados), usando las mismas categorías y filtros.
- **📊 Gráficos Comparativos** — mapa de cuadrantes tipo scouting board: elige cualquier
  métrica para el eje X y cualquier otra para el eje Y (de las 329 disponibles a nivel de
  equipo-temporada), y compara los 20 equipos de LaLiga con líneas de referencia en la
  media o mediana de la liga.

Todas las páginas comparten:
- La misma **biblioteca de equipos** (`data/matches/*.csv`) — un archivo por equipo.
- El mismo panel de **actualización semanal** con fusión sin duplicados por `gameId`.
- **Filtro por entrenador**: si el CSV trae una columna de entrenador (se detecta
  automáticamente probando varios nombres habituales: TeamManager, Manager, Entrenador,
  Coach...), se usa directamente. Si no, puedes etiquetar tramos de fechas a mano.

## Instalación

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit detecta automáticamente la carpeta `pages/` y monta la navegación lateral —
no hace falta configurar nada más.

## Añadir o actualizar un equipo

Desde el panel **"🔄 Actualizar datos de un equipo"** (disponible en Rival y Propio):

1. Elige el equipo existente a actualizar, o "(nuevo equipo)" y escribe su nombre.
2. Sube el CSV que hayas exportado esa semana desde TruMedia/Opta (temporada completa o
   solo los últimos partidos, da igual — se fusiona por `gameId` sin duplicar).
3. Descarga el CSV fusionado que te ofrece la app.
4. Guarda ese archivo en `data/matches/NombreDelEquipo.csv`.

**Si tu export siempre trae la temporada completa hasta la fecha**, puedes saltarte la
fusión y simplemente reemplazar el archivo en `data/matches/` directamente cada semana.

**En local**: con guardar el archivo ya está — recarga la página.
**En Streamlit Community Cloud**: sube ese archivo a la carpeta `data/matches/` de tu
repositorio de GitHub — redespliega solo en 1-2 minutos.

## Estructura de archivos

```
app.py                              # página de bienvenida / índice
common.py                           # catálogo de métricas, carga de datos, filtros compartidos
data.json                           # equipo-temporada de los 20 equipos de LaLiga (benchmarks)
data/matches/*.csv                  # tu biblioteca de partidos, un CSV por equipo
pages/
  1_🔴_Analisis_Rival.py
  2_🔵_Analisis_Propio.py
  3_📊_Graficos_Comparativos.py
requirements.txt
```

## Limitaciones conocidas

- El CSV de partidos no incluye datos individuales de jugadores.
- No hay una métrica única de "% Posesión" total en el export (solo desglosada por zona
  de campo: campo rival / campo defensivo).
- La fusión semanal depende de la columna `gameId` para detectar duplicados.
- El filtro de entrenador por columna automática solo funciona si tu export incluye esa
  columna con uno de los nombres reconocidos; si no, usa el etiquetado manual.
