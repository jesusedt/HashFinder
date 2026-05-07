# HashFinder 🛡️ — Calculador de Hashes & Auditoría de Integridad

**HashFinder ** es una aplicación de escritorio, moderna y de alto rendimiento diseñada en **Python** utilizando **CustomTkinter**. Permite escanear archivos individuales o directorios completos para listar archivos, registrar sus fechas de creación y modificación, y calcular de manera simultánea y rápida sus firmas criptográficas **MD5** y **SHA-256**.

Ideal para auditores de sistemas, ingenieros de seguridad o administradores de infraestructura que necesitan validar la integridad de sus archivos e identificar modificaciones sospechosas en caliente.

---

## ✨ Características Principales

*   **🛡️ Interfaz de Usuario **: Tema oscuro, animaciones de hover, bordes redondeados y tipografía moderna para una experiencia visual.
*   **📂 Selección Dual**: Dos botones independientes para seleccionar mediante diálogos de Windows:
    *   `Carpeta...`: Escanea directorios completos de forma recursiva o no recursiva.
    *   `Archivo...`: Procesa un único archivo específico de manera directa.
*   **⚡ Hilos de Ejecución en Segundo Plano**: El escaneo y cálculo de hashes se realiza en un hilo de fondo. Esto evita que la interfaz gráfica se congele y te permite cancelar el proceso.
*   **🧠 Algoritmo de Hasheo por Bloques**: Lee archivos secuencialmente en ráfagas de **64 KB**. Esto permite procesar archivos de gran tamaño con un consumo mínimo de memoria RAM.
*   **📅 Registro de Fechas Completo**: Extrae de forma automática la **Fecha de Creación** y **Fecha de Modificación** de los archivos para control, analisis y registro.
*   **📊 Panel de Estadísticas**: Muestra en tiempo real:
    *   Cantidad de archivos procesados vs. total.
    *   Tamaño procesado vs. tamaño total.
    *   Velocidad de escaneo (archivos por segundo).
    *   Tiempo transcurrido exacto con barra de progreso interactiva.
*   **🔍 Búsqueda y Filtros al Instante**: Filtra miles de filas por nombre de archivo, ruta relativa, hashes o extensión mientras escribes.
*   **🔀 Ordenamiento por Columnas**: Haz clic en cualquier columna (Nombre, Ruta, Tamaño, Fechas) para ordenar los resultados de forma ascendente o descendente.
*   **📋 Doble Clic para Copiar**: Copia el hash de cualquier archivo directamente al portapapeles con un doble clic en la fila correspondiente.
*   **📥 Exportaciones Nativas**:
    *   `Exportar CSV`: Genera reportes delimitados por punto y coma (`;`).
    *   `Exportar JSON`: Genera un archivo estructurado y jerárquico de metadatos.

---

## 🛠️ Requisitos del Sistema

*   **Python**: Versión 3.8 o superior.
*   **Dependencias**: Únicamente requiere de la biblioteca gráfica moderna `customtkinter`.

---

## 🚀 Instalación y Ejecución

1.  **Clona el Repositorio**:
    ```bash
    git clone https://github.com/jesusedt/HashFinder.git
    cd hashfinder
    ```

2.  **Instala las Dependencias**:
    Utiliza el archivo de requisitos provisto:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicia la Aplicación**:
    Ejecuta el script principal de Python:
    ```bash
    python app.py
    ```

---

## 📁 Estructura del Proyecto (Modular)

El proyecto está diseñado de forma modular para facilitar su mantenimiento y lectura:

```text
├── app.py                # Interfaz gráfica principal (CustomTkinter GUI)
├── hashing_engine.py     # Lógica de escaneo de archivos y cálculo de hashes (MD5/SHA-256)
├── export_manager.py     # Gestor de exportación de reportes (CSV con BOM / JSON estructurado)
├── requirements.txt      # Archivo de dependencias para Pip (customtkinter)
└── README.md             # Documentación detallada del proyecto
```

---

## 📝 Contribuciones y Soporte

Si deseas agregar nuevas funciones, calcular algoritmos adicionales (como SHA-1 o SHA-512) o reportar alguna mejora, siéntete libre de abrir un **Pull Request** o registrar un **Issue**.
