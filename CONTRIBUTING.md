# Guía de contribución — UPROFE

Este documento resume cómo trabajamos los 8 integrantes del grupo sobre el mismo módulo de Odoo. Léelo antes de tu primer commit.

## 1. Convenciones de nombres

- **Modelo técnico**: `upo.<entidad_en_minusculas>`, ej. `upo.profesor`, `upo.detalle_matricula`. Nunca camelCase. En español pero sin acentos ni caracteres especiales.
- **Archivo Python**: un archivo por modelo en `models/<entidad>.py`, registrado en `models/__init__.py` con `from . import <entidad>`.
- **Campos relacionales**: sufijo `_id` para M2O (`grupo_id`), sufijo `_ids` para O2M/M2M (`asistencia_ids`, `tema_ids`).
- **IDs de vistas**: `view_<modelo>_<tipo>` (`view_profesor_tree`, `view_profesor_form`, `view_profesor_calendar`).
- **Archivo de vistas**: `views/<modelo>_views.xml`, uno por modelo — no mezclar varios modelos en el mismo archivo.
- **Commits**: mensaje con el modelo entre corchetes, ej. `[sesion] añade validación de horas y vista calendar`.
- **Ramas**: `feature/<persona>-<modelo>`, ej. `feature/aurelio-sesion`. Una rama corta por modelo, no una rama única por persona.

## 2. Flujo de trabajo

### 2.1 Antes de empezar un modelo nuevo

```bash
git checkout main
git pull origin main
git checkout -b feature/<persona>-<modelo>
```

Esto asegura que partes de la última versión de `main` y trabajas en un espacio aislado que no afecta al código de nadie más.

### 2.2 Mientras trabajas

Commits pequeños y descriptivos (modelo, vistas, etc):

```bash
git add models/<modelo>.py
git commit -m "[<modelo>] añade modelo con campos básicos y relación a X"
```

### 2.3 Al terminar: pull request

El pull request **no se crea con git**, se crea desde la interfaz de GitHub, después de subir la rama:

```bash
git push origin feature/<persona>-<modelo>
```

1. En GitHub, pulsa **Compare & pull request** (o **Pull requests → New pull request**).
2. Confirma `base: main` ← `compare: feature/<persona>-<modelo>`.
3. Título corto: `[<modelo>] modelo, vistas y validaciones`.
4. Descripción:

   ```
   ## Qué incluye
   - Modelo upo.<modelo> ...
   - Vistas tree, form, [calendar/graph/...] ...
   - Validaciones
   - Etc.

   ```
5. Pulsa **Create pull request**.
6. Otra persona del grupo revisa en **Files changed** y pulsa **Review changes → Approve**.
7. Con la aprobación, pulsa **Merge pull request**. Esto fusiona a `main`.

### 2.4 Issues y Project

Los issues y el Project son dos objetos distintos que hay que conectar explícitamente — no van unidos por defecto.

- **Issues** (dentro del repo): cada modelo tiene su propio issue (`Modelo: upo.<modelo>`), asignado a la persona responsable. Son la capa de gestión (qué falta, quién lo hace); las ramas y PRs son la capa de trabajo (el código en sí).

- **Project** (tablero Kanban To do / En progreso / En revisión / Hecho): es la vista de conjunto del trabajo del grupo. Un issue no aparece ahí solo — hay que añadirlo con alguna de estas opciones:

  1. Desde el Project: **+ Add item** → buscar el issue por número o título.

  2. Desde el issue: barra lateral derecha → sección **Projects** → seleccionar el tablero.

  3. **Automática (recomendada para el grupo)**: en el Project, menú **⋯ → Workflows → activar "Auto-add to project"** apuntando a nuestro repositorio. Así cualquier issue nuevo aparece solo en **To do** sin que nadie tenga que acordarse de añadirlo a mano.

- Una vez el issue está en el Project, **el estado de la tarjeta se puede actualizar manualmente** según avance el trabajo:

  - **To do** → trabajo pendiente.
  - **En progreso** → alguien está trabajando en el issue.
  - **En revisión** → el trabajo está terminado y hay un PR abierto para revisarlo.
  - **Hecho** → el trabajo ha sido revisado y completado.

## 3. Reglas de main

- `main` está protegida: nadie hace push directo, todo entra por pull request.
- Se requiere al menos 1 aprobación de otra persona del grupo antes de poder fusionar.

